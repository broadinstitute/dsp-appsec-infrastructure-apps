from codedx_api.APIs.BaseAPIClient import BaseAPIClient
from codedx_api.APIs.ProjectsAPI import Projects

# Actions API Client for Code DX Projects API
class Actions(BaseAPIClient):

	def __init__(self, base, api_key, verbose = False):
		""" Creates an API Client for Code DX Jobs API
			base: String representing base url from Code DX
			api_key: String representing API key from Code DX
			verbose: Boolean - not supported yet
		"""
		super().__init__(base, api_key, verbose)
		self.projects_api = Projects(base, api_key)

	def bulk_status_update(self, proj, status="false-positive", filters={}):
		""" Create a new Analysis Prep associated with a particular project.
			If Git is configured on that project, the new Analysis Prep will automatically initialize an input corresponding to that configuration.
			Accepts project name or id.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/bulk-status-update' % pid
		params = {
			"filter": filters,
			"status": status
		}
		res = self.call("POST", local_url, params)
		return res