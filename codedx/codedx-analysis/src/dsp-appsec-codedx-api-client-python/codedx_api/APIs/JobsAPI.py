from codedx_api.APIs.BaseAPIClient import BaseAPIClient
import json

# Jobs API Client for Code DX Projects API
class Jobs(BaseAPIClient):
	
	def __init__(self, base, api_key, verbose = False):
		""" Creates an API Client for Code DX Jobs API
			base: String representing base url from Code DX
			api_key: String representing API key from Code DX
			verbose: Boolean - not supported yet
		"""
		super().__init__(base, api_key, verbose)


	def job_status(self, jid):
		""" Queries the status of a job
		"""
		self.type_check(jid, str, "JobId")
		local_url = '/api/jobs/%s' % jid
		res = self.call("GET", local_url)
		return res

	def job_result(self, jid, accept='application/json;charset=utf-8'):
		""" Get the result of a job
		"""
		local_url = '/api/jobs/%s/result' % jid
		res = self.call("GET", local_url, content_type=accept)
		return res