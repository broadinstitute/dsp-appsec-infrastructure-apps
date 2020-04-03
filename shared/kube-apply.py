#!/usr/bin/env python3

import os
import re
import subprocess
import sys

os.environ['HTTPS_PROXY'] = 'socks5://localhost:' + os.getenv('PROXY_PORT')

for name in sys.argv[1:]:
    with open(name) as f:
        template = os.path.expandvars(f.read())
        undefined = re.findall(r'\${[^{]+}', template)
        if undefined:
            raise Exception(
                'Undefined variable(s) in {}: {}'.format(name, undefined)
            )
        subprocess.run(
            ['kubectl', 'apply', '-f', '-'],
            input=template.encode(),
            stdout=sys.stdout,
            stderr=sys.stderr,
        ).check_returncode()
