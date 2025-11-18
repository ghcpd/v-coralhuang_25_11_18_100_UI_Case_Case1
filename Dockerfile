FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN chmod +x setup.sh run.sh test.sh
RUN ["bash", "./setup.sh"]

CMD ["bash", "-c", "./test.sh"]
