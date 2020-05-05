from jinja2 import Template
import sys 

with open("./templates/config_map.yaml.jinja2", "r") as job_input: 
    with open("./deployment.yaml", "w") as f: 
        f.write(Template(job_input.read()).render())

with open("./templates/dsde_cronjobs.yaml.jinja2", "r") as job_input: 
    with open("./deployment.yaml", "a") as f: 
        f.write(Template(job_input.read()).render())

with open("./templates/kdux_cronjobs.yaml.jinja2", "r") as job_input: 
    with open("./deployment.yaml", "a") as f: 
        f.write(Template(job_input.read()).render())
