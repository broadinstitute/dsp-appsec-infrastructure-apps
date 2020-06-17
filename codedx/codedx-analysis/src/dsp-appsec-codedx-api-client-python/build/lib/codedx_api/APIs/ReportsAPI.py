from codedx_api.APIs.BaseAPIClient import BaseAPIClient
from codedx_api.APIs.ProjectsAPI import Projects
import json
import re

report_columns = [
      "projectHierarchy",
      "id",
      "creationDate",
      "updateDate",
      "severity",
      "status",
      "cwe",
	  "rule",
      "tool",
      "location",
      "element",
      "loc.path",
      "loc.line"
]

# Reports Client for Code DX Projects API
class Reports(BaseAPIClient):
	
	def __init__(self, base, api_key, verbose = False):
		""" Creates an API Client for Code DX Projects API
				base: String representing base url from Code DX
				api_key: String representing API key from Code DX
				verbose: Boolean - not supported yet

		"""
		super().__init__(base, api_key, verbose)
		self.projects_api = Projects(base, api_key, verbose)

	def report_types(self, proj):
		""" Provides a list of report types for a project. 
			Each report type (pdf, csv, xml, nessus, and nbe) has a different set of configuration options. These configuration options are important with respect to generating a report.
		"""
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/report/types' % pid
		res = self.call("GET", local_url)
		return res

	def generate(self, pid, report_type, config, filters={}):
		""" Allows user to queue a job to generate a report. 
			Each report type has a different set of configuration options that can be obtained from the Report Types endpoint.
		"""
		params = {}
		params["filter"] = filters
		params["config"] = config
		local_url = '/api/projects/%d/report/%s' % (pid, report_type)
		res = self.call("POST", local_url, json=params)
		return res

	def generate_pdf(self, proj, summary_mode="simple", details_mode="with-source", include_result_details=False, include_comments=False, include_request_response=False, filters={}):
		""" Allows user to queue a job to generate a pdf report. Returns jobId and status.
			summary_mode <String>: Executive summary. One of "none", "simple", or "detailed". Default is "simple".
			details_mode <String>: Finding details. One of "none", "simple", or "with-source". Default is "with-source".
			include_result_details <Boolean>: Include result provided details. Default is false.
			include_comments <Boolean>: Include comments. Default is false.
			include_request_response <Boolean>: Include HTTP requests and responses. Default is false.
		"""
		pid = self.projects_api.process_project(proj)
		config = {}
		if summary_mode not in ["none", "simple", "detailed"]: raise Exception("Invalid summary mode input.")
		config["summaryMode"] = summary_mode
		if details_mode not in ["none", "simple", "with-source"]: raise Exception("Invalid details mode input given.")
		config["detailsMode"] = details_mode
		self.type_check(include_result_details, bool, "Include_result_details")
		config["includeResultDetails"] = include_result_details
		self.type_check(include_comments, bool, "Include_comments")
		config["includeComments"] = include_comments
		self.type_check(include_request_response, bool, "include_request_response")
		config["includeRequestResponse"] = include_request_response
		res = self.generate(pid, "pdf", config, filters)
		return res

	def get_csv_columns(self):
		""" Returns a list of optional columns for a project csv report. 
		"""
		return report_columns

	def generate_csv(self, proj, cols=report_columns):
		""" Allows user to queue a job to generate a csv report. Returns jobId and status.
			Accepts a list of columns to include in the report. Default is all columns.
			Call get_csv_columns() to see column options.
		"""
		pid = self.projects_api.process_project(proj)
		config = {}
		if not cols: raise Exception("CSV report needs at least one column.")
		for col in cols:
			if col not in report_columns: raise Exception("Invaild column name.")
		config["columns"] = cols
		res = self.generate(pid, "csv", config)
		return res

	def generate_xml(self, proj, include_standards=False, include_source=False, include_rule_descriptions=True):
		""" Allows user to queue a job to generate an xml report. Returns jobId and status.
			include_standards <Boolean>: List standards violations. Default is fault.
			include_source <Boolean>: Include source code snippets. Default is false.
			include_rule_descriptions <Boolean>: Include rule descriptions. Default is true.
		"""
		pid = self.projects_api.process_project(proj)
		config = {}
		self.type_check(include_standards, bool, "Include_standards")
		config["includeStandards"] = include_standards
		self.type_check(include_source, bool, "Include_source")
		config["includeSource"] = include_source
		self.type_check(include_rule_descriptions, bool, "include_rule_descriptions")
		config["includeRuleDescriptions"] = include_rule_descriptions
		res = self.generate(pid, "xml", config)
		return res

	def generate_nessus(self, proj, default_host=None, operating_system="", mac_address="", netBIOS_name=""):
		""" Allows user to queue a job to generate a nessus report. Returns jobId and status.
			default_host <String>: Default host. Required.
			operating_system <String>: Operating System. Default is "".
			mac_address <String>: mac address. Required.
			netBIOS_name <String>: NetBIOS name. Defualt is "".
		"""
		pid = self.projects_api.process_project(proj)
		config = {}
		self.type_check(default_host, str, "Default_host")
		config["defaultHost"] = default_host
		self.type_check(operating_system, str, "Operating_system")
		config["operatingSystem"] = operating_system
		self.type_check(mac_address, str, "mac_address")
		if re.search(mac_address, "^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$") is None:
			raise Exception("Not a valid mac address.")
		config["macAddress"] = mac_address
		self.type_check(netBIOS_name, str, "netBIOS_name")
		config["netBIOSName"] = netBIOS_name
		res = self.generate(pid, "nessus", config)
		return res

	def generate_nbe(self, proj, host_address=None):
		""" Allows user to queue a job to generate an AlienVault/NBE report. Returns jobId and status.
			host_address <String>: Host IP address. Required.
		"""
		pid = self.projects_api.process_project(proj)
		config = {}
		self.type_check(host_address, str, "Host_address")
		if re.search(host_address, "^((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]))$") is None:
			raise Exception("Not a valid IPv4 address.")
		config["hostAddresss"] = host_address
		res = self.generate(pid, "nbe", config)
		return res