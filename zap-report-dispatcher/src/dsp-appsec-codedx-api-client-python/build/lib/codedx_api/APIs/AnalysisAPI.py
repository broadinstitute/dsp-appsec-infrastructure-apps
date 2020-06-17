from codedx_api.APIs.BaseAPIClient import BaseAPIClient
from codedx_api.APIs.ProjectsAPI import Projects
import json
import os

# Jobs API Client for Code DX Projects API
class Analysis(BaseAPIClient):
	
	def __init__(self, base, api_key, verbose = False):
		""" Creates an API Client for Code DX Jobs API
			base: String representing base url from Code DX
			api_key: String representing API key from Code DX
			verbose: Boolean - not supported yet
		"""
		super().__init__(base, api_key, verbose)
		self.projects_api = Projects(base, api_key)

	def create_analysis(self, proj):
		""" Create a new Analysis Prep associated with a particular project. 
			If Git is configured on that project, the new Analysis Prep will automatically initialize an input corresponding to that configuration.
			Accepts project name or id.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/analysis-prep'
		params = {"projectId": pid}
		res = self.call("POST", local_url, params)
		return res


	def get_prep(self, prep_id):
		""" Get a list of Input IDs and Verification Errors for an Analysis Prep.
			Accepts a string as the prep_id
		"""
		self.type_check(prep_id, str, "Prep_id")
		local_url = '/api/analysis-prep/%s' % prep_id
		res = self.call("GET", local_url)
		return res

	def upload_analysis(self, prep_id, file_name, client_request_id=None):
		""" Analysis Preps should be populated by uploading files to Code Dx.
			Accepts a string as a prep id.
			See https://codedx.com/Documentation/UserGuide.html#ImportingScanResults for a list of file upload formats
		"""
		self.type_check(prep_id, str, "Prep_id")
		local_url = '/api/analysis-prep/%s/upload' % prep_id
		accepted_file_types = {
			'.xml': 'text/xml',
			'.json': 'application/json',
			'.zip': 'application/zip', 
#			'.ozasmt': '', 
			'.csv': 'text/csv', 
			'.txt': 'text/plain', 
#			'.fpr': '', 
#			'.nessus': '', 
#			'.htm': '', 
#			'.tm7': ''
		}
		file_ext = os.path.splitext(file_name)[1]
		if file_ext not in accepted_file_types:
			raise Exception("File type was not accepted.")
		json = {'file_name': file_name, 'file_path': file_name, 'file_type': accepted_file_types[file_ext]}
		if client_request_id is not None and self.type_check(client_request_id, str, "Client_request_id"):
			json['X-Client-Request-Id'] = client_request_id
		res = self.call(method="UPLOAD", local_path=local_url, json=json)
		return res

	def get_input_metadata(self, prep_id, input_id):
		""" Get metadata for a particular input associated with an Analysis Prep.
		"""
		self.type_check(prep_id, str, "Prep_id")
		self.type_check(input_id, str, "Input_id")
		local_url = '/api/analysis-prep/%s/%s' % (prep_id, input_id)
		res = self.call(method="GET", local_path=local_url)
		return res

	def delete_input(self, prep_id, input_id):
		""" Delete input. If the inputId is known (this will be the case most of the time), use the URL that includes an input-id parameter.
		"""
		self.type_check(prep_id, str, "Prep_id")
		self.type_check(input_id, str, "Input_id")
		local_url = '/api/analysis-prep/%s/%s' % (prep_id, input_id)
		res = self.call(method="DELETE", local_path=local_url)
		return res


	def delete_pending(self, prep_id, request_id):
		""" Delete pending input. If an input file has just begun to upload, but that request has not completed and returned an inputId, use the “pending” URL.
			This requires the input upload request to have specified a X-Client-Request-Id header.
		"""
		self.type_check(prep_id, str, "Prep_id")
		self.type_check(request_id, str, "Request_id")
		local_url = '/api/analysis-prep/%s/pending' % prep_id
		headers = {'X-Client-Request-Id': request_id}
		res = self.call(method="DELETE", local_path=local_url, local_headers=headers)
		return res

	def toggle_display_tag(self, prep_id, input_id, tag_id, enabled):
		""" Enable and disable individual display tags on individual prop inputs.
			Disabled tags will cause a file to be treated as if that tag were not there, for analysis purposes. 
		""" 
		self.type_check(prep_id, str, "Prep_id")
		self.type_check(input_id, str, "Input_id")
		self.type_check(tag_id, str, "Tag_id")
		self.type_check(enabled, bool, "Enable/disable boolean")
		local_url = '/api/analysis-prep/%s/%s/tag/%s' % (prep_id, input_id, tag_id)
		params = {"enabled": enabled}
		res = self.call("PUT", local_path=local_url, json=params)
		return res

	def enable_display_tag(self, prep_id, input_id, tag_id):
		""" Enable individual display tags on individual prop inputs.
			Disabled tags will cause a file to be treated as if that tag were not there, for analysis purposes. 
		""" 
		res = self.toggle_display_tag(prep_id, input_id, tag_id, True)
		return res	

	def disable_display_tag(self, prep_id, input_id, tag_id):
		""" Enable individual display tags on individual prop inputs.
			Disabled tags will cause a file to be treated as if that tag were not there, for analysis purposes. 
		""" 
		res = self.toggle_display_tag(prep_id, input_id, tag_id, False)
		return res	

	def run_analysis(self, prep_id):
		""" Once all of the verificationErrors in an Analysis Prep are addressed, an analysis can be started.
		"""
		self.type_check(prep_id, str, "Prep_id")
		local_url = '/api/analysis-prep/%s/analyze' % prep_id
		res = self.call("POST", local_url)
		return res

	def get_all_analysis(self, proj):
		""" Obtain analysis details for a project, such as start and finish times.
		"""
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/analyses' % pid
		res = self.call("GET", local_url)
		return res

	def get_analysis(self, proj, aid):
		""" Obtain analysis details, such as start and finish times.
		"""
		self.type_check(aid, int, "Analysis ID")
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/analyses/%d' % (pid, aid)
		res = self.call("GET", local_url)
		return res

	def name_analysis(self, proj, aid, name):
		""" Set a name for a specific analysis.
		"""
		self.type_check(name, str, "Name")
		self.projects_api.update_projects()
		pid = self.projects_api.process_project(proj)
		local_url = '/api/projects/%d/analyses/%d' % (pid, aid)
		params = {"name": name}
		res = self.call("PUT", local_path=local_url, json=params, content_type=None)
		return res





