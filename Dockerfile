FROM bearstech/debian-dev:buster

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

RUN set -eux \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gcc \
        libc6-dev \
        clang \
    && curl "https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init" > rustup-init \
    && chmod +x rustup-init \
    && ./rustup-init -y --no-modify-path --default-toolchain nightly \
    && rm rustup-init \
    && chmod -R a+w $RUSTUP_HOME $CARGO_HOME \
    && rustup --version \
    && cargo --version \
    && rustc --version \
    && cargo install sonic-server \
    && strip /usr/local/cargo/bin/sonic \
    && mv /usr/local/cargo/bin/sonic /usr/local/bin/sonic \
    && rm -rf /var/lib/apt/lists/*

CMD [ "sonic", "-c", "/etc/sonic.cfg" ]

EXPOSE 1491
