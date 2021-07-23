import datetime
import json
from string import Template

with open('variables.json') as json_file:
    data = json.load(json_file)

# "modules" represent a service in the appsec cluster
formatted_modules = []
for module in data["modules"]:
    formatted_modules.append(f"COPY src/modules/{ module }/Overview.md docs/SDARQ/Modules/{ module }.md")

data["list"] = '\n'.join(formatted_modules)
data["year"] = datetime.datetime.now().year

with open('Dockerfile.template', 'r') as f:
    src = Template(f.read())
    result = src.substitute(data)
    print(result)

with open('Dockerfile', 'w') as f:
    f.write(result)

with open('src/base/docusaurus.config.js.template', 'r') as f:
    src = Template(f.read())
    result = src.substitute(data)

with open('src/base/docusaurus.config.js', 'w') as f:
    f.write(result)
