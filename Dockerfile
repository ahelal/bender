FROM alpine

RUN apk add --update \
    python \
    python-dev \
    py-pip

ADD src/bin /opt/resource/
ADD src/lib /opt/resource/
ADD requirments.txt /tmp

RUN chmod +x /opt/resource/* && \
    pip install -r /tmp/requirments.txt
