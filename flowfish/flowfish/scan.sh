#!/bin/sh

# nmap -sV --script vulners -oX output/all.xml -iL input/all.txt
# python3 report.py < output/all.xml > output/all.json

echo "Checking nmap version..."
nmap -v

echo "Running vulnerability scan on given target..."
python3 entrypoint.py
