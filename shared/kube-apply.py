#!/usr/bin/env python3

import os, subprocess, sys

with open(sys.argv[1]) as f:
  subprocess.run(
    ['kubectl', 'apply', '-f', '-'],
    input=os.path.expandvars(f.read()).encode(),
    stdout=sys.stdout,
    stderr=sys.stderr,
  ).check_returncode()
