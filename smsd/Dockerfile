FROM debian:bookworm-slim AS build

ENV BUILD_PREFIX /usr/local/src

# Install build dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update && \
	apt-get install -y build-essential git cmake pkg-config libpq-dev \
    libcurl4-gnutls-dev libusb-1.0-0-dev libdbi-dev libgudev-1.0-dev libglib2.0-dev unixodbc-dev

WORKDIR ${BUILD_PREFIX}
RUN git clone https://github.com/gammu/gammu.git --branch master --single-branch

RUN mkdir gammu/build
WORKDIR gammu/build
RUN cmake -DCMAKE_INSTALL_PREFIX="/opt/gammu" -DWITH_BLUETOOTH=OFF -DWITH_IRDA=OFF .. && make -j$(nproc)
RUN make test
RUN make install

FROM debian:bookworm-slim AS gammu

RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update && \
	apt-get install -y libpq5 libcurl4 libusb-1.0-0 libdbi1 libgudev-1.0-0 libglib2.0-0 unixodbc && \
	rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/gammu /opt/gammu

RUN echo /opt/gammu/lib > /etc/ld.so.conf.d/gammu.conf && ldconfig

RUN adduser --system --no-create-home --group --disabled-login gammu && adduser gammu dialout
USER gammu

ENTRYPOINT ["/opt/gammu/bin/gammu-smsd"]
