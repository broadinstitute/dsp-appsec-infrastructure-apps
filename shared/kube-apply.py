#!/usr/bin/env python3

import os, subprocess, sys

for name in sys.argv[1:]:
  with open(name) as f:
    template = os.path.expandvars(f.read()).encode()
    undefined = re.findall(r'\${[^{]+}', template):
    if undefined:
      raise 'Undefined variable(s) in ' + name + ': ' + undefined
    subprocess.run(
      ['kubectl', 'apply', '-f', '-'],
      input=template,
      stdout=sys.stdout,
      stderr=sys.stderr,
    ).check_returncode()
