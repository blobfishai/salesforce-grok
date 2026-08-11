# CRMArena parity world: its own org mirror, served over MCP.
FROM python:3.12-slim
WORKDIR /world
COPY server.py soql.py ./
COPY crmarena_data.db ./crmarena_data.db
ENV PORT=8080 CRMARENA_DB=/world/crmarena_data.db
EXPOSE 8080
HEALTHCHECK --interval=3s --timeout=3s --retries=30 --start-period=5s \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health',timeout=2).status==200 else 1)"
CMD ["python3", "server.py"]
