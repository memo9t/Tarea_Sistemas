FROM python:3.11-slim
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir flask requests pandas numpy
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install sentence-transformers

CMD ["python", "app.py"]
