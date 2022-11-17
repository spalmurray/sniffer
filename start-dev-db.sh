#!/bin/bash
sudo docker run --rm --name sniffer -d -p 27017:27017 mongo
