FROM python:2-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./ ./

VOLUME ["/app/posts.db"]
EXPOSE 4001

ENTRYPOINT ["python2", "/app/main.py"]

