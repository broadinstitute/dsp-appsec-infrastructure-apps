from codedx_api import CodeDxAPI
import argparse

base_url = "https://codedx.dsp-appsec.broadinstitute.org/codedx"

# API key and base url from Code DX
parser = argparse.ArgumentParser()
parser.add_argument('api_key', type=str, help='API from Code DX')
parser.add_argument('project', type=str, help='Code DX project name')
args = parser.parse_args()

cdx = CodeDxAPI.CodeDx(base_url, args.api_key)

cdx.update_projects()

if args.project not in list(cdx.projects):
	cdx.create_project(args.project)

cdx.update_statuses(args.project)