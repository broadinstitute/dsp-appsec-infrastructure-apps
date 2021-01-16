#!/usr/bin/env python3

import os
import re
import subprocess
import sys

https_proxy = "socks5://" + \
    os.environ["PROXY_HOST"] + ":" + os.environ["PROXY_PORT"]
env = dict(os.environ, https_proxy=https_proxy)

for name in sys.argv[1:]:
    with open(name) as f:
        template = os.path.expandvars(f.read())
        undefined = re.findall(r'\${[^{]+}', template)
        if undefined:
            raise Exception(
                'Undefined variable(s) in {}: {}'.format(name, undefined)
            )
        subprocess.run(
            ['kubectl', 'apply', '--request-timeout=1m', '-f', '-'],
            input=template.encode(),
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env,
            check=True,
        )
