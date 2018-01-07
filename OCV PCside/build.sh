#!/bin/bash
file="$1"
sudo g++ -o prog $file.cpp `pkg-config opencv --cflags --libs` -L /usr/bin/curl -std=gnu++11 # -lcurl
