#!/usr/bin/env python3

import os, subprocess, sys

for name in sys.argv[1:]:
  with open(name) as f:
    subprocess.run(
      ['kubectl', 'apply', '-f', '-'],
      input=os.path.expandvars(f.read()).encode(),
      stdout=sys.stdout,
      stderr=sys.stderr,
    ).check_returncode()
