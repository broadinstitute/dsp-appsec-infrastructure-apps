from codedx_api.APIs.BaseAPIClient import BaseAPIClient
from codedx_api.APIs.ProjectsAPI import Projects

class Findings(BaseAPIClient):
	
	def __init__(self, base, api_key, verbose = False):
		super().__init__(base, api_key, verbose)
		self.projects_api = Projects(base, api_key)
	
	def get_finding(self, fid, options=[]):
		""" Returns metadata for the given finding.
			Can include a list of optional expanders to include more information
			Available values: descriptions, descriptor, issue, triage-time, results, results.descriptions, results.descriptor, results.metadata, results.variants
		"""
		self.type_check(fid, int, "Findings ID")
		local_url = '/api/findings/%d' % fid
		self.type_check(options, list, "Optional expanders")
		if len(options) > 0:
			query = '?expand=' + options.pop(0)
			while(len(options) > 0):
				query = query + "," + options.pop(0)
			local_url = local_url + query
		res = self.call("GET", local_url)
		return res

	def get_finding_description(self, fid):
		""" Returns the descriptions for the given finding from all available sources.
		"""
		self.type_check(fid, int, "Findings ID")
		local_url = '/api/findings/%d/description' % fid
		res = self.call("GET", local_url)
		return res

	def get_finding_history(self, fid):
		""" Responds with an array of “activity event” objects in JSON.
		"""
		self.type_check(fid, int, "Findings ID")
		local_url = '/api/findings/%d/history' % fid
		res = self.call("GET", local_url)
		return res

	def get_finding_table(self, proj, options=[], query={}):
		""" Returns filtered finding table data.
			This endpoint is a candidate to become a more generic querying API; presently it just returns the data required for the findings table as it exists today.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/findings/table' % pid
		self.type_check(options, list, "Optional expanders")
		if len(options) > 0:
			query = '?expand=' + options.pop(0)
			while(len(options) > 0):
				query = query + "," + options.pop(0)
			local_url = local_url + query
		if query:
			params = {"query": query}
			res = self.call("POST", local_path=local_url, json=params)
		else:
			res = self.call("POST", local_url)
		return res

	def get_finding_count(self, proj, query={}):
		""" Returns the count of all findings in the project matching the given filter.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/findings/count' % pid
		if query:
			params = {"query": query}
			res = self.call("POST", local_path=local_url, json=params)
		else:
			res = self.call("POST", local_url)
		return res

	def get_finding_group_count(self, proj, query={}):
		""" Returns filtered finding table data.
			This endpoint is a candidate to become a more generic querying API; presently it just returns the data required for the findings table as it exists today.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/findings/grouped-counts' % pid
		if query:
			params = {"query": query}
			res = self.call("POST", local_path=local_url, json=params)
		else:
			res = self.call("POST", local_url)
		return res

	def get_finding_flow(self, proj, flow_req={}):
		""" Returns filtered finding table data.
			This endpoint is a candidate to become a more generic querying API; presently it just returns the data required for the findings table as it exists today.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/findings/flow' % pid
		if flow_req:
			params = {"flowRequest": flow_req}
			res = self.call("POST", local_path=local_url, json=params)
		else:
			res = self.call("POST", local_url)
		return res

	def get_finding_file(self, proj, path):
		""" Returns the contents of a given file, as long as it is a text file.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		if isinstance(path, str):
			local_url = '/api/projects/%d/files/%s' % (pid, path)
		elif isinstance(path, int):
			local_url = '/api/projects/%d/files/%d' % (pid, path)
		else:
			raise Exception("File path must be either string or int.")
		res = self.call("GET", local_url)
		return res