FROM alpine:latest AS builder

RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app

RUN python3 -m venv venv

COPY requirements.txt .

RUN /app/venv/bin/pip3 install -r requirements.txt

FROM alpine:latest

EXPOSE 5000

LABEL org.opencontainers.image.authors="jurica.zrna@true-north.hr" \
      org.opencontainers.image.vendor="True North"

ENV DB_USER=animal \
    DB_PASSWORD=secret \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DB_NAME=animals \
    APP_SETTINGS=config.Config

RUN apk add --no-cache python3

WORKDIR /app

COPY app.py config.py ./

COPY data /app/data

COPY --from=builder /app/venv /app/venv

ENTRYPOINT ["/app/venv/bin/python3"]

CMD ["app.py"]
