#!/usr/bin/env python3

import os, subprocess, sys

with open(sys.argv[1]) as f:
  subprocess.run(
    ['kubectl', 'apply', '-f', '-'],
    input=os.path.expandvars(f),
    stdout=sys.stdout,
    stderr=sys.stderr,
    encoding='ascii',
  ).check_returncode()
