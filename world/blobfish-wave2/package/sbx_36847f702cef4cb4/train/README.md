# Train and evaluate a model on this world

This world is an RL gym: every task has an executable verifier, and the
bundle ships reference trajectories that this kit replays from a fresh seed
and re-verifies before use. It turns only those fresh verifier passes
into a measured SFT + GRPO before/after experiment on a small open model —
keyless, fully local, and judged only by the world's own verifiers. Results
may improve, regress, or remain flat; the scorecard determines the claim.

```bash
# 1. Validate the training data (stdlib only, seconds)
python3 train/run_training_eval.py --dry-run

# 2. Validate the eval harness end-to-end without any ML deps (stdlib only)
python3 train/run_training_eval.py --policy oracle

# 3. Measure a small Qwen before and after training (installs: pip install -r train/requirements.txt)
python3 train/run_training_eval.py --smoke          # bounded experiment
python3 train/run_training_eval.py                  # Qwen3-0.6B: SFT then one GRPO round
python3 train/run_training_eval.py --grpo-rounds 2  # a larger grouped-policy run
python3 train/run_training_eval.py --model Qwen/Qwen3-8B   # pinned revision, substantial GPU memory
python3 train/run_training_eval.py --model Qwen/Qwen3-14B  # pinned revision, substantial GPU memory
```

## What it does

1. Replays candidate traces on a fresh seed and builds `train/sft.jsonl` only from
   task-matched trajectories that pass the executable verifier again.
2. Splits tasks deterministically into train / held-out (held-out tasks contribute zero training data).
3. Evaluates the base model on held-out tasks: ReAct rollouts over the world's executable tools,
   pass/fail decided by each task's executable VCode verifier.
4. LoRA-SFTs the model on the verified traces (the Agent-World paper's SFT cold-start stage).
5. Evaluates the SFT checkpoint, then samples fresh groups of eight environment rollouts
   per train task and applies clipped group-relative policy updates (0.20/0.28).
6. Re-evaluates the same held-out tasks and writes `train/scorecard.json` + `train/REPORT.md`
   with base → SFT → GRPO deltas and variable-group/KL evidence.

## Outputs

- `train/sft.jsonl` — verified SFT data (OpenAI-messages format, ReAct tool calls)
- `train/scorecard.json` — machine-readable base vs tuned held-out results
- `train/REPORT.md` — the human-readable before/after table
- `train/eval_episodes.jsonl` — every eval episode with per-step tool calls + verifier verdicts
- `train/adapter/` — the trained LoRA adapter

World: morgan_stanley_simulated (`sbx_36847f702cef4cb4`). Default model: Qwen/Qwen3-0.6B at an immutable
revision. Qwen3-8B and Qwen3-14B are also revision-pinned; other HF chat models work
via `--model` + `--revision`. Training-time tool execution and verification import the
bundle's own `reference_rollout.py`, so the training contract is byte-identical to the runtime.
This scorecard is a local holdout for this gym, not a claim that the paper's multi-environment
40K-SFT/5K-RL/eight-repeat external benchmark result has been reproduced.
