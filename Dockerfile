FROM docker.ocf.berkeley.edu/theocf/debian:stretch

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        cracklib-runtime \
        libcrack2-dev \
        libffi-dev \
        libssl-dev \
        python3.7-dev \
        redis-tools \
        runit \
        sudo \
        virtualenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN install -d --owner=nobody /opt/create /opt/create/venv

COPY requirements.txt /opt/create/
RUN virtualenv -ppython3.7 /opt/create/venv \
    && /opt/create/venv/bin/pip install pip==8.1.2 \
    && /opt/create/venv/bin/pip install \
        -r /opt/create/requirements.txt

COPY etc/sudoers /etc/sudoers.d/create
# Added for dev-wporr
COPY etc/dev-create.conf /opt/create/
COPY create /opt/create/create

# TODO: remove this after ocflib no longer calls nscd
RUN ln -s /bin/true /usr/sbin/nscd

COPY services /opt/create/services
RUN chown -R nobody:nogroup /opt/create/services

USER nobody
WORKDIR /opt/create
ENV PATH=/opt/create/venv/bin:$PATH
CMD ["runsv", "services/create"]
