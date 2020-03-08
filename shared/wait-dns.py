#!/usr/bin/env python3

import os, socket, time

IP_ADDRESS = os.getenv('IP_ADDRESS')
DNS_HOSTNAME = os.getenv('DNS_HOSTNAME')

while True:
  try:
    if IP_ADDRESS == socket.gethostbyname(DNS_HOSTNAME):
      break
  except:
    time.sleep(5)
