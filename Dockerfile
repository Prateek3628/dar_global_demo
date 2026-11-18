FROM python:3.11-slim
WORKDIR /app
COPY app.py scrape.py index.html ./
COPY data/corpus.json data/
ENV PORT=8080
EXPOSE 8080
CMD ["python", "app.py"]
