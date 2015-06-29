#!/bin/bash

ROOT="$1"
ISO_PROGRAM=$ROOT/tm-git/src/isolists

cd $ISO_PROGRAM
python po-to-table.py
