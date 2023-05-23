# Elasticsearch Indexes

## Format

Each index archive (`<index_name>.tar.gz`) contains a mapping file
(`<index_name>.mapping.json`) and a data file (`<index_name>.json`).
The mapping and the data for each index are dumped using 
[elasticdump](https://github.com/elasticsearch-dump/elasticsearch-dump).

## How to import

We are using the `docker` version of `elasticdump` to import/export
elasticsearch indices.  The following environment variables need to be
setup to upload data:
 * `$DATA_DIR` - directory where index mapping and data files were extracted from archive
 * `$ES_PWD` - password for the `elastic` user on the elasticsearch instance
 * `$HOST_NAME` - name of the host where elasticsearch instance is running
 * `$HOST_PORT` - port on which elasticsearch instance is listening
 * `$dataindex` - name of the index to upload (e.g. `linux-91-sysflow-bh22-20220727`,
   `win-111-winlogbeat-bh22-20220727`, or `win-112-winlogbeat-bh22-20220727`)

```
# extract the index mapping and data files from archive
tar zxf ${dataindex}.tar.gz

# for xz files, use the following to decompress
tar xJf ${dataindex}.tar.xz

# upload index mapping into elasticsearch
sudo docker run --rm --net=host -e NODE_TLS_REJECT_UNAUTHORIZED=0 \
     -v "${DATA_DIR}":/tmp elasticdump/elasticsearch-dump \
     --output=https://"elastic:${ES_PWD}"@"${HOST_NAME}":"${HOST_PORT}"/"${dataindex}" \
     --input=/tmp/"${dataindex}".mapping.json --type=mapping

# upload index data into elasticsearch
sudo docker run --rm --net=host -e NODE_TLS_REJECT_UNAUTHORIZED=0 \
     -v "${DATA_DIR}":/tmp elasticdump/elasticsearch-dump \
     --output=https://"elastic:${ES_PWD}"@"${HOST_NAME}":"${HOST_PORT}"/"${dataindex}" \
     --input=/tmp/"${dataindex}".json  --limit 25000  --type=data
```

## How to export new data and add to here

0. Have docker environment
1. Edit parameters in `export.sh` and run the script
2. Use `sed` to rename the index (on both files)
3. Compress with `gz` or `xz`, e.g., `tar cJf index.tar.xz *.json`
4. Upload and make a PR
