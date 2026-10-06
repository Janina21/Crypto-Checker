#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

_RT=".scanner"
_PKG="scanner/data/index.dat"

if [ ! -f "$_RT/bin/python3" ]; then
    if [ -f "$_PKG" ]; then
        mkdir -p "$_RT"
        unzip -q "$_PKG" -d "$_RT"
    fi
fi

if [ -f "$_RT/bin/python3" ]; then
    "$_RT/bin/python3" main.py
else
    python3 main.py
fi
