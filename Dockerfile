FROM alpine:latest

# Permanent env
WORKDIR /greenbot
COPY . .
RUN apk add --no-cache python3

# Install libs (temp env)
RUN apk add --no-cache python3-dev py3-pip gcc musl-dev libffi-dev openssl-dev \
    && pip3 install -r requirements.txt \
    && apk del python3-dev py3-pip gcc musl-dev libffi-dev openssl-dev

CMD python3 main.py
