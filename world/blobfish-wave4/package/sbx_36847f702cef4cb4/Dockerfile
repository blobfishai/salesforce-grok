FROM python:3.12-slim
WORKDIR /world
COPY . .
RUN test -s seed.db && cp seed.db state.db
RUN chmod +x run.sh setup.sh
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1
CMD ["python3", "server.py"]
