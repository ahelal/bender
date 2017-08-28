FROM alpine:3.6

RUN apk add --update \
    python \
    python-dev \
    py-pip

ADD src/bin /opt/resource/
ADD src/lib /opt/resource/
ADD requirements.txt /tmp

RUN chmod +x /opt/resource/* \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Do some clean up
RUN echo "# Cleaning up" && echo "" \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache/
