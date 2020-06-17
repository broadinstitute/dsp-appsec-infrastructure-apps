from codedx_api import CodeDxAPI
import argparse

base_url = "https://codedx.dsp-appsec.broadinstitute.org/codedx"

parser = argparse.ArgumentParser()
parser.add_argument('api_key', type=str, help='API key from Code DX')
parser.add_argument('project', type=str, help='Code DX project name or id')
parser.add_argument('file_name', type=str, help='File name to upload')
args = parser.parse_args()

cdx = CodeDxAPI.CodeDx(base_url, args.api_key)

res = cdx.analyze(args.project, args.file_name)
