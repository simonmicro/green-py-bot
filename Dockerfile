FROM alpine:latest

# Permanent env
WORKDIR /greenbot
COPY .git ./.git
COPY greenbot ./greenbot
COPY main.py .
COPY requirements.txt .
RUN apk add --no-cache python3 git

# Install libs (temp env)
RUN apk add --no-cache python3-dev py3-pip gcc musl-dev libffi-dev openssl-dev \
    && pip3 install -r requirements.txt \
    && apk del --no-cache python3-dev gcc musl-dev libffi-dev openssl-dev

RUN rm requirements.txt

CMD python3 main.py
