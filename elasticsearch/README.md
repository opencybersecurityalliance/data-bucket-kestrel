# Elasticsearch Indexes

## Format

Indexes are dumped using [elastictl](https://github.com/binwiederhier/elastictl).

## How to import

```
zcat index.json.gz | elastictl import --host user:pwd@your.elastic.server:9200 index 
```

Note that the vanilla `elastictl` [does not support HTTPS](https://github.com/binwiederhier/elastictl/issues/4). To import data to Elasticsearch with HTTPS enabled (default in `Elasticsearch >= 8`), please compile the [https branch @ subbyte fork](https://github.com/subbyte/elastictl/tree/https) to use.

If you are using a self-signed certificate, please install that certificate into
your OS to avoid certificate verification error, e.g., on Debian:
1. Copy certificate file to `/usr/local/share/ca-certificates`
2. Run `update-ca-certificates` as root
