from codedx_api import CodeDxAPI
from datetime import date
import argparse

base_url = "https://codedx.dsp-appsec.broadinstitute.org/codedx"

# API key and base url from Code DX
parser = argparse.ArgumentParser()
parser.add_argument('api_key', type=str, help='Base url from Code DX')
parser.add_argument('project', type=str, help='Code DX project name or id')
args = parser.parse_args()

cdx = CodeDxAPI.CodeDx(base_url, args.api_key)

report_title = args.project + '_report_' + date.today().strftime("%b%d%y") + ".pdf"

res = cdx.get_pdf(args.project, summary_mode="detailed", details_mode="with-source", include_result_details=True, include_comments=True, include_request_response=False, file_name=report_title)