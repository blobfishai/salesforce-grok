#!/usr/bin/env python3
"""Run a held-out training evaluation on THIS world - keyless and self-contained.

The same stage order Blobfish runs internally (and the Agent-World paper uses,
arXiv:2604.18292): SFT cold-start from verifier-passed traces, followed by
group-relative policy optimization from fresh environment rollouts. Every
reward and every number in train/scorecard.json is produced by the bundle's
OWN tools and VCode verifiers - no API keys, no LLM judge.

Stages:
  1. Build train/sft.jsonl from the bundle's VERIFIED trajectories
     (only verifier-passed episodes ever become training data).
  2. Split tasks deterministically into train / held-out. Held-out tasks
     contribute NO training data.
  3. Evaluate the BASE model on the held-out tasks (ReAct rollout over the
     world's executable tools; the task's executable verifier decides pass/fail).
  4. LoRA-SFT the model on the verified traces.
  5. Re-evaluate after SFT, then run GRPO groups on TRAIN tasks only. Each
     group uses fresh copy-on-write state and executable reward; groups with
     no reward variance are skipped rather than faking an update.
  6. Re-evaluate the SAME held-out tasks -> train/scorecard.json +
     train/REPORT.md with base -> SFT -> GRPO deltas.

Usage:
  python3 train/run_training_eval.py --dry-run          # stdlib only: build + validate data
  python3 train/run_training_eval.py --policy oracle    # stdlib only: validate the eval harness
  python3 train/run_training_eval.py --smoke            # bounded experiment (small caps)
  python3 train/run_training_eval.py                    # full run (default small Qwen)
  python3 train/run_training_eval.py --model Qwen/Qwen3-1.7B --grpo-rounds 2
  python3 train/run_training_eval.py --model Qwen/Qwen3-8B
  python3 train/run_training_eval.py --model Qwen/Qwen3-14B

Model deps (full run only): pip install -r train/requirements.txt
"""
import argparse, contextlib, json, math, os, random, re, shutil, sys, tempfile, time

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, ROOT)

try:
    import reference_rollout as rr
except Exception as e:  # pragma: no cover - packaging guard
    print("[train-kit] FATAL: could not import reference_rollout.py from the bundle root: " + str(e))
    print("[train-kit] Run this script from an extracted world bundle (train/run_training_eval.py).")
    sys.exit(2)

DEFAULT_MODEL = "Qwen/Qwen3-0.6B"
PINNED_MODEL_REVISIONS = {
    "Qwen/Qwen3-0.6B": "c1899de289a04d12100db370d81485cdf75e47ca",
    "Qwen/Qwen3-8B": "b968826d9c46dd6066d109eabc6255188de91218",
    "Qwen/Qwen3-14B": "40c069824f4251a91eefaf281ebe4c544efd3e18",
}
SCORECARD_SCHEMA = "blobfish.train-scorecard.v1"
CLAIM_SCOPE = "single_downloaded_gym_local_holdout_not_full_paper_reproduction"
TOOL_MENU_LIMIT = 48


def log(msg):
    print("[train-kit] " + msg, flush=True)


def load_world():
    with open(os.path.join(ROOT, "world.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Prompt rendering — the ONE renderer used for BOTH training data and eval
# rollouts (train/serve parity: a tuned model sees exactly the format it was
# trained on).
# ---------------------------------------------------------------------------

def system_prompt(world):
    company = (world.get("thesis") or {}).get("company") or "the company"
    return (
        "You are an operations agent for " + company + ". You act ONLY by emitting tool calls as JSON. "
        'Respond with EXACTLY ONE JSON object per turn: {"tool": "<name>", "arguments": {...}} to call a tool, '
        'or {"answer": "<short summary>"} when the task is complete.'
    )


def _words(value):
    return set(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def task_tools(world, task, limit=TOOL_MENU_LIMIT):
    """Bound the Forge-era catalog without dropping task-critical tools.

    Composite companies can expose hundreds of operations. Sending every tool
    makes native-FC prompts exceed 32k tokens. Rank deterministic distractors
    from task/tool semantics and retain every executable reference tool, while
    preserving world-catalog order so the menu does not reveal solution order.
    """
    all_tools = world.get("tools", [])
    sequence = task.get("walk") or task.get("_reference_tools") or task.get("required_tools") or []
    required = set(str(name) for name in sequence)
    task_terms = _words(task.get("prompt"))
    ranked = []
    for index, tool in enumerate(all_tools):
        text = " ".join([
            str(tool.get("name") or ""), str(tool.get("description") or ""),
            " ".join(str(name) for name in (tool.get("target_tables") or [])), str(tool.get("forge_service") or ""),
        ])
        score = len(task_terms & _words(text))
        ranked.append((-score, index, tool.get("name")))
    distractor_budget = max(0, limit - len(required))
    distractors = {name for _, _, name in sorted(ranked) if name not in required}
    if len(distractors) > distractor_budget:
        ordered = [name for _, _, name in sorted(ranked) if name not in required]
        distractors = set(ordered[:distractor_budget])
    selected = required | distractors
    return [tool for tool in all_tools if tool.get("name") in selected]


def tools_block(world, task):
    lines = []
    for t in task_tools(world, task):
        params = (t.get("parameters") or {})
        rendered = ", ".join(k + ": " + str(v) for k, v in params.items()) if params else "none"
        description = str(t.get("description") or "")[:180]
        lines.append("- " + t["name"] + " (" + t.get("type", "read") + ") - " + description + " | parameters: " + rendered[:240])
    return "\n".join(lines)


def task_user_message(world, task):
    return (
        "AVAILABLE TOOLS:\n(task-scoped retrieval from the full company catalog)\n" + tools_block(world, task)
        + "\n\nTASK: " + (task.get("prompt") or "")
        + '\n\nComplete the task with tool calls, then emit {"answer": "..."}.'
    )


def action_json(tool, arguments):
    return json.dumps({"tool": tool, "arguments": arguments}, sort_keys=True, default=str)


# ---------------------------------------------------------------------------
# SFT data from verified trajectories
# ---------------------------------------------------------------------------

def executable_verifier_evidence(traj):
    """Return the task-matched verifier record or fail closed.

    A stored passed flag is not evidence. Candidates need an explicit verifier
    basis, a matching executable-verifier result, matching verdict/reward, and
    structurally valid assertions. Every candidate is then replayed against a
    fresh database below before it can enter SFT.
    """
    basis = traj.get("verification_basis")
    if basis == "vcode":
        verifier = traj.get("vcode_verifier")
    elif basis == "executable_state_assertions":
        verifier = traj.get("verifier")
    else:
        return None
    if not isinstance(verifier, dict) or verifier.get("error"):
        return None
    task_id = traj.get("task_id")
    if not task_id or verifier.get("task_id") != task_id:
        return None
    if verifier.get("passed") is not True or traj.get("passed") is not True:
        return None
    try:
        if abs(float(verifier.get("reward")) - float(traj.get("reward"))) > 1e-9:
            return None
    except (TypeError, ValueError):
        return None
    assertions = verifier.get("assertions")
    if not isinstance(assertions, list):
        return None
    for assertion in assertions:
        if not isinstance(assertion, dict) or not assertion.get("name") or not isinstance(assertion.get("passed"), bool):
            return None
    return verifier


def attested_trajectories_by_task(world):
    out = {}
    for traj in world.get("trajectories") or []:
        if not isinstance(traj, dict):
            continue
        tid = traj.get("task_id")
        steps = traj.get("steps") or []
        if not tid or not steps or executable_verifier_evidence(traj) is None:
            continue
        out.setdefault(tid, traj)
    return out


def ensure_trajectories(world):
    """Replay evidence and self-heal missing or forged reference traces.

    Static verifier fields are only admission candidates. The bundled tools and
    VCode are replayed on a fresh DB; only fresh passes can become SFT examples.
    """
    embedded_count = len(world.get("trajectories") or [])
    candidates = attested_trajectories_by_task(world)
    attested_records = sum(
        1 for trajectory in (world.get("trajectories") or [])
        if isinstance(trajectory, dict) and trajectory.get("steps") and executable_verifier_evidence(trajectory) is not None
    )
    by_task, rejected = replay_trajectory_evidence(world, candidates)
    expected = {v.get("task_id") for v in world.get("verifiers") or [] if v.get("task_id") and v.get("vcode")}
    missing = sorted(expected - set(by_task))
    stats = {
        "embedded_records": embedded_count,
        "attested_records": attested_records,
        "attested_task_candidates": len(candidates),
        "ignored_duplicate_attested_records": max(0, attested_records - len(candidates)),
        "fresh_replay_passes": len(by_task),
        "rejected_embedded": len(rejected) + max(0, embedded_count - attested_records),
        "regenerated": False,
        "missing_task_ids": missing,
    }
    if not missing:
        return world, by_task, stats
    log("missing fresh verifier-passed evidence for %d task(s) - regenerating locally via reference_rollout.py" % len(missing))
    import subprocess
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "reference_rollout.py"), os.path.join(ROOT, "world.json"), str(len(world.get("tasks", [])))],
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode == 0:
            trajs = json.loads(r.stdout).get("trajectories") or []
            world = dict(world)
            world["trajectories"] = trajs
            with open(os.path.join(BASE, "trajectories_local.jsonl"), "w") as f:
                for t in trajs:
                    f.write(json.dumps(t, default=str) + "\n")
            candidates = attested_trajectories_by_task(world)
            regenerated_attested_records = sum(
                1 for trajectory in trajs
                if isinstance(trajectory, dict) and trajectory.get("steps") and executable_verifier_evidence(trajectory) is not None
            )
            by_task, regenerated_rejected = replay_trajectory_evidence(world, candidates)
            stats.update({
                "regenerated": True,
                "regenerated_records": len(trajs),
                "regenerated_attested_records": regenerated_attested_records,
                "regenerated_replay_passes": len(by_task),
                "regenerated_rejected": len(regenerated_rejected) + max(0, len(trajs) - regenerated_attested_records),
                "missing_task_ids": sorted(expected - set(by_task)),
            })
            log("regenerated %d trajectories (%d fresh verifier replays passed)" % (len(trajs), len(by_task)))
        else:
            log("local reference rollout failed rc=" + str(r.returncode) + ": " + (r.stderr or "")[:200])
    except Exception as e:
        log("local reference rollout failed: " + str(e)[:200])
    return world, by_task, stats


def episode_to_messages(world, task, steps):
    msgs = [
        {"role": "system", "content": system_prompt(world)},
        {"role": "user", "content": task_user_message(world, task)},
    ]
    for s in steps:
        args = s.get("args")
        if args is None:
            args = s.get("arguments") or {}
        msgs.append({"role": "assistant", "content": action_json(s.get("tool"), args)})
        msgs.append({"role": "user", "content": "OBSERVATION: " + str(s.get("observation") or "")[:300]})
    msgs.append({"role": "assistant", "content": json.dumps({"answer": "Completed all required steps; workflow state updated."})})
    return msgs


def build_sft_examples(world, train_task_ids, by_task):
    tasks = {t["task_id"]: t for t in world.get("tasks", [])}
    examples = []
    for tid in train_task_ids:
        traj = by_task.get(tid)
        task = tasks.get(tid)
        if not traj or not task:
            continue
        examples.append({
            "messages": episode_to_messages(world, task, traj.get("steps") or []),
            "metadata": {
                "teacher": "reference_oracle",
                "world_id": world.get("world_id"),
                "task_id": tid,
                "verified": True,
                "reward": traj.get("reward", 1.0),
            },
        })
    return examples


# ---------------------------------------------------------------------------
# Episode runner — same execution + verification contract as the shipped
# runtime (reference_rollout.py functions).
# ---------------------------------------------------------------------------

def parse_action(text):
    """Extract the first balanced JSON object from model output."""
    if not text:
        return None
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                        return obj if isinstance(obj, dict) else None
                    except Exception:
                        break
        start = text.find("{", start + 1)
    return None


def task_step_budget(task, cap):
    seq = task.get("walk") or task.get("_reference_tools") or task.get("required_tools") or []
    return max(4, min(cap, len(seq) + 3))


def run_episode(world, task, generate_fn, seed_db_path, workdir, max_steps):
    state = os.path.join(workdir, "ep_" + str(task.get("task_id")) + ".db")
    shutil.copy2(seed_db_path, state)
    initial = rr.snapshot(state)
    msgs = [
        {"role": "system", "content": system_prompt(world)},
        {"role": "user", "content": task_user_message(world, task)},
    ]
    steps = []
    trace = []
    policy_segments = []
    answered = False
    for _ in range(max_steps):
        prompt_messages = [dict(message) for message in msgs]
        text = generate_fn(msgs)
        policy_segments.append({"messages": prompt_messages, "output": text})
        action = parse_action(text)
        if not action:
            break
        if "answer" in action:
            answered = True
            break
        tool = action.get("tool")
        args = action.get("arguments")
        if not isinstance(args, dict):
            args = {}
        r = rr.execute_tool(world, state, str(tool), args)
        result = r.get("result")
        obs = (json.dumps(result, default=str) if result is not None else str(r.get("error")))[:300]
        steps.append({"step": len(steps) + 1, "tool": str(tool), "args": args, "ok": bool(r.get("ok")), "observation": obs})
        trace.append({"tool": str(tool), "ok": bool(r.get("ok"))})
        msgs.append({"role": "assistant", "content": action_json(str(tool), args)})
        msgs.append({"role": "user", "content": "OBSERVATION: " + obs})
    final = rr.snapshot(state)
    vr = rr.run_verifier(world, task["task_id"], initial, final, trace)
    try:
        os.remove(state)
    except OSError:
        pass
    try:
        reward = float(vr.get("reward") or 0.0)
    except (TypeError, ValueError):
        reward = 0.0
    return {
        "task_id": task["task_id"],
        "passed": bool(vr.get("passed")),
        "reward": reward,
        "answered": answered,
        "steps": steps,
        "policy_segments": policy_segments,
        "verifier": {k: vr.get(k) for k in ("passed", "reward", "failed_conditions", "explanation", "error")},
    }


class OraclePolicy:
    """Replays a verified trajectory's actions — proves the eval harness
    (rollout loop + tool execution + verifier) end-to-end with zero ML deps."""

    def __init__(self, steps):
        self.actions = [
            {"tool": s.get("tool"), "arguments": (s.get("args") if s.get("args") is not None else s.get("arguments")) or {}}
            for s in steps
        ]
        self.i = 0

    def __call__(self, messages):
        if self.i < len(self.actions):
            a = self.actions[self.i]
            self.i += 1
            return action_json(a["tool"], a["arguments"])
        return json.dumps({"answer": "done"})


def replay_trajectory_evidence(world, candidates):
    """Re-run every candidate from a clean seed and keep fresh VCode passes."""
    if not candidates:
        return {}, []
    task_map = {task.get("task_id"): task for task in world.get("tasks") or []}
    workdir = tempfile.mkdtemp(prefix="train-evidence-")
    seed_db_path = os.path.join(workdir, "seed.db")
    accepted = {}
    rejected = []
    try:
        rr.seed_db(seed_db_path, world)
        for task_id, trajectory in candidates.items():
            task = task_map.get(task_id)
            if not task:
                rejected.append({"task_id": task_id, "reason": "task_missing"})
                continue
            policy = OraclePolicy(trajectory.get("steps") or [])
            budget = max(task_step_budget(task, max(10, len(policy.actions) + 1)), len(policy.actions) + 1)
            episode = run_episode(world, task, policy, seed_db_path, workdir, budget)
            if episode.get("passed"):
                accepted[task_id] = trajectory
            else:
                rejected.append({
                    "task_id": task_id,
                    "trajectory_id": trajectory.get("id"),
                    "reason": "fresh_verifier_replay_failed",
                })
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return accepted, rejected


def evaluate(world, tasks, policy_for_task, seed_db_path, workdir, max_step_cap, label):
    per_task = {}
    episodes = []
    passed = 0
    for idx, task in enumerate(tasks, 1):
        generate_fn = policy_for_task(task)
        budget = task_step_budget(task, max_step_cap)
        if isinstance(generate_fn, OraclePolicy):
            budget = max(budget, len(generate_fn.actions) + 1)
        ep = run_episode(world, task, generate_fn, seed_db_path, workdir, budget)
        ep["phase"] = label
        per_task[task["task_id"]] = ep["passed"]
        episodes.append(ep)
        if ep["passed"]:
            passed += 1
        log("  %s %d/%d %s -> %s (reward %.2f)" % (label, idx, len(tasks), task["task_id"], "PASS" if ep["passed"] else "FAIL", ep.get("reward") or 0.0))
    total = len(tasks)
    return {
        "passed": passed,
        "total": total,
        "rate": round(passed / total, 4) if total else 0.0,
        "per_task": per_task,
    }, episodes


# ---------------------------------------------------------------------------
# Torch/peft backend (imported only for real model runs)
# ---------------------------------------------------------------------------

class TorchBackend:
    def __init__(self, model_id, revision, seed, max_len):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except Exception as e:
            print("[train-kit] Missing model deps (" + str(e) + ").")
            print("[train-kit] Install them with: pip install -r train/requirements.txt")
            sys.exit(2)
        self.torch = torch
        self.max_len = max_len
        random.seed(seed)
        torch.manual_seed(seed)
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
        dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        revision_note = " @ " + revision if revision else " @ unpinned main"
        log("loading " + model_id + revision_note + " on " + self.device + " (" + str(dtype).replace("torch.", "") + ")")
        load_kwargs = {"revision": revision} if revision else {}
        self.tok = AutoTokenizer.from_pretrained(model_id, **load_kwargs)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, **load_kwargs).to(self.device)
        self.requested_revision = revision
        self.resolved_revision = getattr(self.model.config, "_commit_hash", None) or revision
        self.model.eval()
        self._peft_wrapped = False

    def _generate(self, messages, max_new_tokens, do_sample, temperature):
        # return_dict=True: transformers versions differ on whether a bare
        # tensor or a BatchEncoding comes back - request the dict explicitly.
        enc = self.tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_tensors="pt", return_dict=True)
        ids = enc["input_ids"].to(self.device)
        attn = enc.get("attention_mask")
        attn = attn.to(self.device) if attn is not None else self.torch.ones_like(ids)
        prompt_budget = max(1, self.max_len - max_new_tokens)
        if ids.shape[1] > prompt_budget:
            # Preserve the BOS token plus the recent task/observations. The
            # task is deliberately rendered after the tool menu, so it cannot
            # disappear when a long multi-turn history is compacted.
            if prompt_budget > 1:
                ids = self.torch.cat([ids[:, :1], ids[:, -(prompt_budget - 1):]], dim=1)
                attn = self.torch.cat([attn[:, :1], attn[:, -(prompt_budget - 1):]], dim=1)
            else:
                ids = ids[:, -1:]
                attn = attn[:, -1:]
        kwargs = {"max_new_tokens": max_new_tokens, "pad_token_id": self.tok.pad_token_id, "attention_mask": attn}
        if do_sample:
            kwargs.update({"do_sample": True, "temperature": temperature, "top_p": 0.95})
        else:
            kwargs.update({"do_sample": False})
        with self.torch.no_grad():
            out = self.model.generate(ids, **kwargs)
        return self.tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)

    def generate(self, messages, max_new_tokens=160):
        return self._generate(messages, max_new_tokens, False, None)

    def sample(self, messages, temperature=0.8, max_new_tokens=160):
        return self._generate(messages, max_new_tokens, True, temperature)

    def _encode(self, messages):
        """One bounded SFT window per assistant turn.

        Head truncation silently masked every label when the task/tool prompt
        alone exceeded max_len. Each window keeps recent context and the full
        assistant segment, so every returned sample has trainable tokens.
        """
        prefix = []
        windows = []
        prev = ""
        for i in range(len(messages)):
            cur = self.tok.apply_chat_template(messages[: i + 1], tokenize=False, add_generation_prompt=False)
            seg = cur[len(prev):]
            seg_ids = self.tok(seg, add_special_tokens=False).input_ids
            if messages[i]["role"] == "assistant":
                completion = list(seg_ids[-max(1, self.max_len - 1):])
                context_budget = max(0, self.max_len - len(completion))
                context = prefix[-context_budget:] if context_budget else []
                ids = context + completion
                labels = [-100] * len(context) + completion
                if completion:
                    windows.append((ids, labels))
            prefix.extend(seg_ids)
            prev = cur
        return windows

    def ensure_lora(self):
        if self._peft_wrapped:
            return
        try:
            from peft import LoraConfig, get_peft_model
        except Exception as e:
            print("[train-kit] Missing peft (" + str(e) + "). Install: pip install -r train/requirements.txt")
            sys.exit(2)
        # LoRA scale (alpha/rank) 20 is the internally proven small-data config;
        # scale 2 demonstrably under-learns on gym-sized datasets.
        cfg = LoraConfig(r=8, lora_alpha=160, lora_dropout=0.05, task_type="CAUSAL_LM",
                         target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
        self.model = get_peft_model(self.model, cfg)
        self._peft_wrapped = True

    def train(self, examples, epochs, lr):
        self.ensure_lora()
        torch = self.torch
        encoded = [window for example in examples for window in self._encode(example["messages"])]
        encoded = [(i, l) for i, l in encoded if any(x != -100 for x in l)]
        if not encoded:
            log("no trainable tokens after encoding - aborting train stage")
            return 0.0
        log("  encoded %d assistant windows; every window retains trainable labels" % len(encoded))
        params = [p for p in self.model.parameters() if p.requires_grad]
        opt = torch.optim.AdamW(params, lr=lr)
        # Gradients remain enabled in eval mode. Keeping dropout disabled makes
        # the first policy ratio exactly comparable to the rollout-time old
        # policy snapshot instead of adding adapter-dropout noise.
        self.model.eval()
        order = list(range(len(encoded)))
        last = 0.0
        for ep in range(1, epochs + 1):
            random.shuffle(order)
            total = 0.0
            for j in order:
                ids, labels = encoded[j]
                input_ids = torch.tensor([ids], device=self.device)
                label_ids = torch.tensor([labels], device=self.device)
                out = self.model(input_ids=input_ids, labels=label_ids)
                out.loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
                opt.zero_grad()
                total += float(out.loss.detach())
            last = total / len(order)
            log("  epoch %d/%d loss %.4f" % (ep, epochs, last))
        self.model.eval()
        return last

    def _segment_logprob(self, messages, output):
        """Mean policy log-probability for one generated assistant segment.

        The prompt is treated as context and only tokens emitted by the policy
        contribute. Computing each ReAct turn separately avoids training on
        tool observations while preserving the exact history seen at rollout.
        """
        torch = self.torch
        prefix = self.tok.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
        )
        if hasattr(prefix, "tolist"):
            prefix = prefix.tolist()
        if prefix and isinstance(prefix[0], list):
            prefix = prefix[0]
        completion = self.tok(output, add_special_tokens=False).input_ids
        if self.tok.eos_token_id is not None:
            completion = completion + [self.tok.eos_token_id]
        if not completion:
            return None
        keep_prefix = max(1, self.max_len - len(completion))
        prefix = list(prefix)[-keep_prefix:]
        completion = completion[: max(1, self.max_len - len(prefix))]
        ids = prefix + completion
        if len(ids) < 2 or not completion:
            return None
        input_ids = torch.tensor([ids], device=self.device)
        logits = self.model(input_ids=input_ids).logits[:, :-1, :]
        targets = input_ids[:, 1:]
        token_logps = torch.log_softmax(logits, dim=-1).gather(
            -1, targets.unsqueeze(-1)
        ).squeeze(-1)
        start = max(0, len(prefix) - 1)
        chosen = token_logps[:, start:]
        if chosen.numel() == 0:
            return None
        return chosen.mean()

    def _trajectory_logprob(self, policy_segments):
        values = []
        for segment in policy_segments:
            value = self._segment_logprob(
                segment.get("messages") or [], str(segment.get("output") or "")
            )
            if value is not None:
                values.append(value)
        if not values:
            return None
        return self.torch.stack(values).mean()

    def _reference_context(self):
        if self._peft_wrapped and hasattr(self.model, "disable_adapter"):
            return self.model.disable_adapter()
        return contextlib.nullcontext()

    def prepare_grpo_group(self, episodes):
        """Attach group-normalized advantages plus old/reference log-probs."""
        self.ensure_lora()
        usable = [episode for episode in episodes if episode.get("policy_segments")]
        if len(usable) < 2:
            return []
        rewards = [float(episode.get("reward") or 0.0) for episode in usable]
        mean = sum(rewards) / len(rewards)
        variance = sum((reward - mean) ** 2 for reward in rewards) / len(rewards)
        std = math.sqrt(variance)
        if std < 1e-6:
            return []
        prepared = []
        self.model.eval()
        for episode, reward in zip(usable, rewards):
            with self.torch.no_grad():
                old = self._trajectory_logprob(episode["policy_segments"])
                with self._reference_context():
                    reference = self._trajectory_logprob(episode["policy_segments"])
            if old is None or reference is None:
                continue
            prepared.append({
                "policy_segments": episode["policy_segments"],
                "reward": reward,
                "advantage": (reward - mean) / std,
                "old_logp": float(old.detach()),
                "reference_logp": float(reference.detach()),
            })
        return prepared

    def grpo_update(self, samples, epochs, lr, clip_low, clip_high, beta):
        """Compact GRPO update over complete multi-turn environment rollouts.

        It uses the paper's asymmetric clip bounds, a frozen base-policy KL
        reference, group-normalized advantages, and no value model. The ratio
        is trajectory-level (mean assistant-token log-probability), which keeps
        the downloadable implementation small while retaining the defining
        grouped policy-gradient mechanics.
        """
        if not samples:
            return {"samples": 0, "loss": None, "mean_kl": None}
        self.ensure_lora()
        torch = self.torch
        params = [parameter for parameter in self.model.parameters() if parameter.requires_grad]
        opt = torch.optim.AdamW(params, lr=lr)
        losses = []
        kls = []
        # Gradients remain enabled in eval mode. Keep LoRA dropout disabled so
        # the first update compares the exact rollout policy to its stored old
        # log-probability instead of injecting an unrecorded dropout policy.
        self.model.eval()
        for _ in range(epochs):
            random.shuffle(samples)
            for sample in samples:
                current = self._trajectory_logprob(sample["policy_segments"])
                if current is None:
                    continue
                old = torch.tensor(sample["old_logp"], device=self.device)
                reference = torch.tensor(sample["reference_logp"], device=self.device)
                advantage = torch.tensor(sample["advantage"], device=self.device)
                ratio = torch.exp(torch.clamp(current - old, -10.0, 10.0))
                clipped = torch.clamp(ratio, 1.0 - clip_low, 1.0 + clip_high)
                surrogate = torch.minimum(ratio * advantage, clipped * advantage)
                ref_delta = torch.clamp(reference - current, -10.0, 10.0)
                kl = torch.exp(ref_delta) - ref_delta - 1.0
                loss = -surrogate + beta * kl
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
                opt.zero_grad()
                losses.append(float(loss.detach()))
                kls.append(float(kl.detach()))
        self.model.eval()
        return {
            "samples": len(samples),
            "loss": round(sum(losses) / len(losses), 6) if losses else None,
            "mean_kl": round(sum(kls) / len(kls), 6) if kls else None,
        }

    def save_adapter(self, out_dir):
        if not self._peft_wrapped:
            return
        try:
            self.model.save_pretrained(out_dir)
            log("adapter saved to " + out_dir)
        except Exception as e:
            log("adapter save skipped: " + str(e)[:120])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_scorecard(payload):
    path = os.path.join(BASE, "scorecard.json")
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    log("scorecard written: " + path)


def write_report(payload):
    lines = [
        "# Training evaluation report - " + str(payload.get("world_id")),
        "",
        "Model: " + str(payload.get("model")) + "  |  device: " + str(payload.get("device")) + "  |  seed: " + str(payload.get("seed")),
        "",
        "| phase | held-out passed | rate |",
        "|-------|-----------------|------|",
    ]
    base = payload.get("baseline") or {}
    after_sft = payload.get("after_sft") or {}
    tuned = payload.get("tuned") or {}
    after_rft = payload.get("after_rft") or {}
    lines.append("| base | " + str(base.get("passed")) + "/" + str(base.get("total")) + " | " + str(base.get("rate")) + " |")
    if after_sft:
        lines.append("| after SFT | " + str(after_sft.get("passed")) + "/" + str(after_sft.get("total")) + " | " + str(after_sft.get("rate")) + " |")
    if tuned:
        lines.append("| after GRPO | " + str(tuned.get("passed")) + "/" + str(tuned.get("total")) + " | " + str(tuned.get("rate")) + " |")
        if after_rft:
            lines.append("| after optional RFT | " + str(after_rft.get("passed")) + "/" + str(after_rft.get("total")) + " | " + str(after_rft.get("rate")) + " |")
        lines.append("")
        lines.append("Delta: **" + str(payload.get("delta_pp")) + "pp** on held-out tasks this model never trained on.")
        lines.append("GRPO-only delta after the SFT checkpoint: **" + str(payload.get("grpo_delta_pp")) + "pp**.")
    lines.append("")
    lines.append("Every verdict above comes from the world's own executable verifiers (reference_rollout.run_verifier) - no LLM judge, no API keys.")
    lines.append("")
    lines.append("Outcome boundary: this experiment may improve, regress, or remain flat. The measured scorecard determines the claim; the training recipe does not guarantee lift.")
    lines.append("")
    lines.append("Claim scope: this is a local held-out result for one downloaded gym. It is not the paper's 1,978-environment, 40K-SFT, 5K-RL, eight-repeat benchmark reproduction.")
    with open(os.path.join(BASE, "REPORT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Measure SFT and GRPO before/after results on this world")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--revision", default=None, help="immutable Hugging Face model revision (known Qwen targets are pinned by default)")
    ap.add_argument("--policy", choices=["model", "oracle"], default="model")
    ap.add_argument("--dry-run", action="store_true", help="build + validate training data only (stdlib)")
    ap.add_argument("--smoke", action="store_true", help="small caps for a bounded experiment run")
    ap.add_argument("--skip-train", action="store_true", help="baseline eval only")
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--heldout", type=int, default=0, help="held-out task count (default ~30%%, 2..6)")
    ap.add_argument("--max-steps", type=int, default=10)
    ap.add_argument("--max-len", type=int, default=3072)
    ap.add_argument("--grpo-rounds", type=int, default=1, help="group-relative policy rounds after SFT")
    ap.add_argument("--grpo-group", type=int, default=8, help="fresh rollouts per task group (paper uses 8)")
    ap.add_argument("--grpo-epochs", type=int, default=2)
    ap.add_argument("--grpo-lr", type=float, default=1e-5)
    ap.add_argument("--grpo-temperature", type=float, default=0.8)
    ap.add_argument("--grpo-beta", type=float, default=0.01)
    ap.add_argument("--clip-low", type=float, default=0.20)
    ap.add_argument("--clip-high", type=float, default=0.28)
    ap.add_argument("--rft-rounds", type=int, default=0, help="optional rejection-filtered SFT rounds; this is not GRPO")
    ap.add_argument("--rft-group", type=int, default=4)
    ap.add_argument("--rft-temperature", type=float, default=0.8)
    args = ap.parse_args()

    t0 = time.time()
    world = load_world()
    rng = random.Random(args.seed)
    requested_revision = args.revision or PINNED_MODEL_REVISIONS.get(args.model)

    verifier_ids = {v.get("task_id") for v in world.get("verifiers", []) if v.get("vcode")}
    tasks = [t for t in world.get("tasks", []) if t.get("task_id") in verifier_ids]
    if not tasks:
        log("this world ships no verifiable tasks - nothing to train against")
        write_scorecard({"schema": SCORECARD_SCHEMA, "status": "no_verifiable_tasks", "world_id": world.get("world_id")})
        sys.exit(3)

    world, by_task, evidence_stats = ensure_trajectories(world)
    ids = sorted(t["task_id"] for t in tasks)
    rng.shuffle(ids)
    heldout_n = args.heldout or max(2, min(6, round(len(ids) * 0.3)))
    heldout_n = min(heldout_n, max(1, len(ids) - 1))
    heldout_ids = set(ids[:heldout_n])
    train_ids = [i for i in ids if i not in heldout_ids]
    if args.smoke:
        train_ids = train_ids[:8]
        heldout_ids = set(sorted(heldout_ids)[:4])

    task_map = {t["task_id"]: t for t in tasks}
    heldout_tasks = [task_map[i] for i in sorted(heldout_ids)]
    if args.policy == "oracle":
        heldout_tasks = [t for t in heldout_tasks if t["task_id"] in by_task]

    examples = build_sft_examples(world, train_ids, by_task)
    sft_path = os.path.join(BASE, "sft.jsonl")
    with open(sft_path, "w") as f:
        for e in examples:
            f.write(json.dumps(e, default=str) + "\n")
    log("world %s: %d verifiable tasks | %d train / %d held-out | %d verified SFT examples -> %s" % (
        world.get("world_id"), len(tasks), len(train_ids), len(heldout_ids), len(examples), sft_path))

    base_payload = {
        "schema": SCORECARD_SCHEMA,
        "world_id": world.get("world_id"),
        "model": args.model if args.policy == "model" else "oracle-replay",
        "requested_model_revision": requested_revision if args.policy == "model" else None,
        "seed": args.seed,
        "claim_scope": CLAIM_SCOPE,
        "recipe": "SFT_then_GRPO",
        "data": {
            "sft_examples": len(examples),
            "train_tasks": len(train_ids),
            "heldout_tasks": len(heldout_ids),
            "verified_source": "freshly replayed task-matched executable verifier trajectories only",
            "trajectory_evidence": evidence_stats,
        },
    }

    if args.dry_run:
        base_payload.update({"status": "dry_run", "python": sys.version.split()[0]})
        write_scorecard(base_payload)
        if not examples:
            log("WARNING: no verified trajectories in this bundle - re-download the world or run reference_rollout.py first")
        log("dry run complete (%.1fs)" % (time.time() - t0))
        return

    workdir = tempfile.mkdtemp(prefix="train-kit-")
    seed_db = os.path.join(workdir, "seed.db")
    rr.seed_db(seed_db, world)
    try:
        if args.policy == "oracle":
            log("oracle harness validation: replaying verified trajectories through the eval loop")
            policy_for_task = lambda task: OraclePolicy((by_task.get(task["task_id"]) or {}).get("steps") or [])
            baseline, episodes = evaluate(world, heldout_tasks, policy_for_task, seed_db, workdir, args.max_steps, "oracle")
            base_payload.update({"status": "oracle_eval", "baseline": baseline, "device": "none", "wall_seconds": round(time.time() - t0, 1)})
            write_scorecard(base_payload)
            _dump_episodes(episodes)
            log("oracle pass-rate %s/%s - the eval harness and verifiers are live" % (baseline["passed"], baseline["total"]))
            return

        backend = TorchBackend(args.model, requested_revision, args.seed, args.max_len)
        base_payload["device"] = backend.device
        base_payload["resolved_model_revision"] = backend.resolved_revision

        log("baseline eval on %d held-out tasks" % len(heldout_tasks))
        policy_for_task = lambda task: (lambda msgs: backend.generate(msgs))
        baseline, base_eps = evaluate(world, heldout_tasks, policy_for_task, seed_db, workdir, args.max_steps, "base")
        base_payload["baseline"] = baseline

        if args.skip_train:
            base_payload.update({"status": "baseline_only", "wall_seconds": round(time.time() - t0, 1)})
            write_scorecard(base_payload)
            _dump_episodes(base_eps)
            return

        if not examples:
            base_payload.update({"status": "no_training_data", "wall_seconds": round(time.time() - t0, 1)})
            write_scorecard(base_payload)
            log("no verified SFT examples - cannot train. Run python3 reference_rollout.py world.json to regenerate trajectories.")
            sys.exit(3)

        log("SFT: %d examples, %d epochs, lr %s" % (len(examples), args.epochs, args.lr))
        backend.train(examples, args.epochs, args.lr)

        log("held-out eval after SFT")
        after_sft, sft_eps = evaluate(
            world, heldout_tasks, policy_for_task, seed_db, workdir,
            args.max_steps, "after_sft"
        )

        grpo_rounds = max(0, args.grpo_rounds)
        grpo_group = max(2, args.grpo_group)
        if args.smoke:
            grpo_rounds = min(grpo_rounds, 1)
            grpo_group = min(grpo_group, 4)
        grpo_stats = []
        for rnd in range(1, grpo_rounds + 1):
            log("GRPO round %d: %d fresh rollouts/task on %d train tasks" % (
                rnd, grpo_group, len(train_ids)
            ))
            prepared = []
            attempted_groups = 0
            variable_groups = 0
            mean_rewards = []
            for tid in train_ids:
                task = task_map[tid]
                episodes = []
                for _ in range(grpo_group):
                    episodes.append(run_episode(
                        world, task,
                        lambda msgs: backend.sample(msgs, args.grpo_temperature),
                        seed_db, workdir, task_step_budget(task, args.max_steps),
                    ))
                attempted_groups += 1
                rewards = [float(episode.get("reward") or 0.0) for episode in episodes]
                mean_rewards.append(sum(rewards) / len(rewards))
                group = backend.prepare_grpo_group(episodes)
                if group:
                    variable_groups += 1
                    prepared.extend(group)
            update = backend.grpo_update(
                prepared, args.grpo_epochs, args.grpo_lr,
                args.clip_low, args.clip_high, args.grpo_beta,
            )
            round_stats = {
                "round": rnd,
                "attempted_groups": attempted_groups,
                "variable_groups": variable_groups,
                "skipped_constant_groups": attempted_groups - variable_groups,
                "mean_reward": round(sum(mean_rewards) / len(mean_rewards), 4) if mean_rewards else 0.0,
                "group_size": grpo_group,
                "clip_low": args.clip_low,
                "clip_high": args.clip_high,
                "beta": args.grpo_beta,
                **update,
            }
            grpo_stats.append(round_stats)
            log("  variable groups %d/%d, samples %d, mean KL %s" % (
                variable_groups, attempted_groups, update.get("samples") or 0,
                str(update.get("mean_kl")),
            ))

        # Measure the GRPO checkpoint before any optional rejection-filtered
        # fine-tuning so grpo_delta_pp is causally attributable to GRPO.
        log("held-out eval after GRPO")
        tuned, tuned_eps = evaluate(
            world, heldout_tasks, policy_for_task, seed_db, workdir,
            args.max_steps, "after_grpo"
        )

        pool = list(examples)
        rft_stats = []
        for rnd in range(1, args.rft_rounds + 1):
            log("RFT round %d: sampling %d rollouts/task on %d train tasks" % (rnd, args.rft_group, len(train_ids)))
            new = []
            for tid in train_ids:
                task = task_map[tid]
                for _ in range(args.rft_group):
                    ep = run_episode(world, task, lambda msgs: backend.sample(msgs, args.rft_temperature),
                                     seed_db, workdir, task_step_budget(task, args.max_steps))
                    if ep["passed"] and ep["steps"]:
                        new.append({"messages": episode_to_messages(world, task, ep["steps"]),
                                    "metadata": {"teacher": "self_rft_round_" + str(rnd), "task_id": tid, "verified": True}})
            rft_stats.append({"round": rnd, "kept": len(new)})
            log("  kept %d verifier-passed self-samples" % len(new))
            if not new:
                continue
            pool = pool + new
            backend.train(pool, max(2, args.epochs // 2), args.lr)

        after_rft = None
        rft_eps = []
        if rft_stats:
            log("held-out eval after optional rejection-filtered fine-tuning")
            after_rft, rft_eps = evaluate(
                world, heldout_tasks, policy_for_task, seed_db, workdir,
                args.max_steps, "after_rft"
            )

        delta_pp = round((tuned["rate"] - baseline["rate"]) * 100, 1)
        grpo_delta_pp = round((tuned["rate"] - after_sft["rate"]) * 100, 1)
        base_payload.update({
            "status": "ok",
            "after_sft": after_sft,
            "tuned": tuned,
            "delta_pp": delta_pp,
            "grpo_delta_pp": grpo_delta_pp,
            "grpo": grpo_stats,
            "rft": rft_stats,
            "after_rft": after_rft,
            "wall_seconds": round(time.time() - t0, 1),
        })
        write_scorecard(base_payload)
        write_report(base_payload)
        backend.save_adapter(os.path.join(BASE, "adapter"))
        _dump_episodes(base_eps + sft_eps + tuned_eps + rft_eps)
        log("RESULT: base %d/%d -> SFT %d/%d -> GRPO %d/%d on held-out tasks (total %+.1fpp, GRPO %+.1fpp)" % (
            baseline["passed"], baseline["total"], after_sft["passed"], after_sft["total"],
            tuned["passed"], tuned["total"], delta_pp, grpo_delta_pp))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _dump_episodes(episodes):
    path = os.path.join(BASE, "eval_episodes.jsonl")
    with open(path, "w") as f:
        for ep in episodes:
            f.write(json.dumps(ep, default=str) + "\n")
    log("episodes written: " + path)


if __name__ == "__main__":
    main()
