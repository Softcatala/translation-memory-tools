#!/bin/bash

if [[ "$(docker ps -q -f name=translation-memory-tools 2> /dev/null)" != "" ]]; then
    echo Stopping translation-memory-tools running container
    docker stop translation-memory-tools
fi

if [[ "$(docker container ls -a -q -f name=translation-memory-tools  2> /dev/null)" != "" ]]; then
    echo Removing translation-memory-tools container
    docker container rm translation-memory-tools
fi

if [[ "$(docker ps -q -f name=translation-memory-tools-lt 2> /dev/null)" != "" ]]; then
    echo Stopping translation-memory-tools-lt running container
    docker stop translation-memory-tools-lt
fi

if [[ "$(docker container ls -a -q -f name=translation-memory-tools-lt  2> /dev/null)" != "" ]]; then
    echo Removing translation-memory-tools-lt container
    docker container rm translation-memory-tools-lt
fi

echo "Finish stop script"
exit 0
