# Shared world image: the whole simulated company, served as REST + MCP.
#
# Build context is populated by scripts/build-images.sh, which copies the chosen
# world package (world.json, seed.db, tools/, server.py, isolation.py, tasks.jsonl)
# into ./payload. The image is built once and referenced by every task's compose
# file, so a task directory stays a few kilobytes instead of carrying a 15 MB world.
FROM python:3.12-slim

WORKDIR /world
COPY payload/ /world/

# state.db is the mutable copy the agent writes to; seed.db stays pristine so the
# verifier can diff against it and `POST /reset` can restore between trials.
RUN test -s seed.db && cp seed.db state.db

ENV PORT=8080
EXPOSE 8080
HEALTHCHECK --interval=3s --timeout=3s --retries=30 --start-period=5s \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health',timeout=2).status==200 else 1)"
CMD ["python3", "harbor_server.py"]
