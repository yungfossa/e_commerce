FROM postgres:14-alpine

# install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    git \
    make \
    gcc \
    libc-dev \
    postgresql-dev

# clone pg_ulid
RUN git clone https://github.com/andrielfn/pg-ulid.git /tmp/pg_ulid

# manually build and install pg_ulid
RUN cd /tmp/pg_ulid && \
    gcc -fPIC -I $(pg_config --includedir-server) -c ulid.c && \
    gcc -fPIC -shared -o ulid.so ulid.o && \
    cp ulid.so $(pg_config --pkglibdir) && \
    cp ulid.control $(pg_config --sharedir)/extension/ && \
    cp ulid--0.0.1.sql $(pg_config --sharedir)/extension/ && \
    cd / && \
    rm -rf /tmp/pg_ulid

# remove build dependencies
RUN apk del .build-deps

# add extension to default database
RUN echo "CREATE EXTENSION ulid;" > /docker-entrypoint-initdb.d/init-ulid-extension.sql
