#!/bin/bash

if [ -z ${1+x} ]; then
    echo "Usage: $0 ADDRESS put|get ...";
    exit 1;
fi
if [ -z ${2+x} ]; then
    echo "Usage: $0 ADDRESS put|get ...";
    exit 1;
fi

addr="$1"

case $2 in
    get)
        if [ -z ${3+x} ]; then
            echo "Usage: $0 $1 get ID";
            exit 1;
        fi
        id=$3
        curl -X GET "http://${addr}:4001/get" -H "Content-Type: application/json" \
            --data "{\"post_id\": ${id}}"
    ;;
    put)
        if [ -z ${3+x} ]; then
            echo "Usage: $0 $1 get TITLE CONTENT IS_PUBLIC";
            exit 1;
        fi
        title="$3"
        if [ -z ${4+x} ]; then
            echo "Usage: $0 $1 get TITLE CONTENT IS_PUBLIC";
            exit 1;
        fi
        content="$4"
        if [ -z ${5+x} ]; then
            echo "Usage: $0 $1 get TITLE CONTENT IS_PUBLIC";
            exit 1;
        fi
        public="$5"
        curl -X POST "http://${addr}:4001/store" -H "Content-Type: application/json" \
            --data "{\"title\": \"${title}\", \"content\": \"${content}\", \"public\": \"${public}\"}"
    ;;
esac
