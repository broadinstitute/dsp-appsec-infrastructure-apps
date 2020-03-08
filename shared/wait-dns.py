#!/usr/bin/env python3

import os, socket, sys, time

IP_ADDRESS = sys.argv[1]
DNS_HOSTNAMES = sys.argv[2:]

for hostname in DNS_HOSTNAMES:
  while True:
    try:
      if IP_ADDRESS == socket.gethostbyname(hostname):
        break
    except:
      time.sleep(5)
