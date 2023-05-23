#!/usr/bin/env sh

DATA_DIR=$(pwd)
HOST_NAME=192.168.1.100
HOST_PORT=9200
ES_USER=elastic
ES_PWD=xxx
INDEX_NAME=logs-windows.sysmon_operational-default
BATCH_SIZE=10000
REC_COUNT=500000

echo "[Info] The script will export the mapping and data of index: $INDEX_NAME"
echo "[Info] Both mapping and data will be saved to $DATA_DIR"
echo "[Info] At most $REC_COUNT Elasticsearch documents will be exported in batch of $BATCH_SIZE"

docker run --rm --net=host -ti \
  -e NODE_TLS_REJECT_UNAUTHORIZED=0 \
  -v $DATA_DIR:/tmp \
  elasticdump/elasticsearch-dump \
  --input=https://"${ES_USER}:${ES_PWD}"@"${HOST_NAME}":"${HOST_PORT}"/"${INDEX_NAME}" \
  --output=/tmp/$INDEX_NAME.mapping.json \
  --type=mapping

docker run --rm --net=host -ti \
  -e NODE_TLS_REJECT_UNAUTHORIZED=0 \
  -v $DATA_DIR:/tmp \
  elasticdump/elasticsearch-dump \
  --input=https://"${ES_USER}:${ES_PWD}"@"${HOST_NAME}":"${HOST_PORT}"/"${INDEX_NAME}" \
  --output=/tmp/$INDEX_NAME.json \
  --limit=$BATCH_SIZE \
  --size=$REC_COUNT \
  --type=data

