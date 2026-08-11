FROM python:3.12-slim
WORKDIR /srv
COPY gateway.py .
ENV PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=3s --timeout=3s --retries=20 --start-period=5s \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=2).status==200 else 1)"
CMD ["python3", "gateway.py"]
