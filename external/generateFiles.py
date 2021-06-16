from string import Template
import json
import datetime

d = {
    'title': 'This is the title',
    'subtitle': 'And this is the subtitle',
    'list': '\n'.join(['COPY package.json .', 'COPY sidebars.js', 'third'])
}

with open('variables.json') as json_file:
    data = json.load(json_file)

formatted_modules = []
for module in data["modules"]:
    formatted_modules.append(f"COPY modules/{ module } docs/SDARQ/Modules/.")

data["list"] = '\n'.join(formatted_modules)
data["year"] = datetime.datetime.now().year

with open('Dockerfile.template', 'r') as f:
    src = Template(f.read())
    result = src.substitute(data)
    print(result)

with open('Dockerfile', 'w') as f:
    f.write(result)

with open('docusaurus.config.js.template', 'r') as f:
    src = Template(f.read())
    result = src.substitute(data)

with open('docusaurus.config.js', 'w') as f:
    f.write(result)