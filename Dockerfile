FROM bearstech/debian-dev:buster as build

ARG VERSION=1.3.0

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
    && cargo install --version ${VERSION} sonic-server \
    && strip /usr/local/cargo/bin/sonic

FROM bearstech/debian-dev:buster

COPY --from=build /usr/local/cargo/bin/sonic /usr/local/bin/sonic

CMD [ "/usr/local/bin/sonic", "-c", "/etc/sonic.cfg" ]

EXPOSE 1491

ARG GIT_VERSION
ARG GIT_DATE
ARG BUILD_DATE

LABEL \
    com.bearstech.image.revision_date=${GIT_DATE} \
    org.opencontainers.image.authors=Bearstech \
    org.opencontainers.image.revision=${GIT_VERSION} \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.url=https://github.com/factorysh/aio-sonic-rest \
    org.opencontainers.image.source=https://github.com/factorysh/aio-sonic-rest/blob/${GIT_VERSION}/Dockerfile
