FROM nginx:1.12.1-alpine-perl
COPY patches/*.patch /tmp/
RUN apk add --no-cache \
        build-base \
        ca-certificates \
        fcgiwrap \
        make \
        openssl \
        perl-carp \
        perl-cgi \
        perl-net-dns \
        perl-uri \
        sudo \
        tini \
        wget \
 && update-ca-certificates \
 && wget https://github.com/pacparser/pacparser/releases/download/1.3.7/pacparser-1.3.7.tar.gz -O pacparser-1.3.7.tar.gz \
 && sh -c 'tar xzf pacparser-1.3.7.tar.gz && \
             cd pacparser* && \
             cat /tmp/*.patch | patch -p1 && \
             cd src && \
             make && \
             make install' \
 && rm -rf pacparser* /tmp/*.patch
ENTRYPOINT ["/sbin/tini", "--"]
COPY nginx-conf/*.conf /etc/nginx/conf.d/
COPY pactester.cgi /usr/lib/cgi-bin/pactester-cgi/pactester.cgi

CMD ["/bin/sh", "-c", "sudo -u nginx sh -c 'while true; do /usr/bin/fcgiwrap -s unix:/tmp/fcgiwrap.socket; done' & exec nginx -g 'daemon off;'"]

