import sys
import requests
import json
import csv	

class BaseAPIClient(object):

	def __init__(self, base, api_key, verbose = False):
		self.verbose = verbose
		self.base_path = base
		self.api_key = api_key
		self.headers = {
			'API-Key': self.api_key, 
			'accept': 'application/json', 
			'Content-Type': 'application/json'
		}
		self.commands = {
			"GET": self._get,
			"POST": self._post,
			"PUT": self._put,
			"DELETE": self._delete,
			"UPLOAD": self._upload
		}

	def _compose_url(self,local_path):
		return self.base_path + local_path

	def _compose_headers(self,local_headers):
		headers = self.headers
		for key in local_headers:
			headers[key] = local_headers[key]
		return headers

	def type_check(self, inp, t, field):
		if not isinstance(inp, t):
			msg = "%s is not of type %s" % (field, t)
			raise Exception(msg)
			return False
		return True

	def _get(self, url, headers, json, content_type):
		res = APIResponse(requests.get(url, headers=headers), content_type)
		return res.getData()

	def _post(self, url, headers, json, content_type):
		res = APIResponse(requests.post(url, headers=headers, json=json), content_type)
		return res.getData()

	def _upload(self, url, headers, json, content_type):
		if 'file_name' not in json or 'file_path' not in json or 'file_type' not in json:
			raise Exception("Missing file data.")
		headers = {'API-Key': self.api_key, 
			'accept': 'application/json'}
		if 'X-Client-Request-Id' in json:
			headers['X-Client-Request-Id'] = json['X-Client-Request-Id']
		f = open(json['file_path'], 'rb')
		files = {
			'file': (json['file_name'], f, json['file_type'])
		}
		res = APIResponse(requests.post(url, headers=headers, files=files), content_type)
		f.close()
		return res.getData()

	def _put(self, url, headers, json, content_type):		
		if self.verbose:
			req = requests.Request('PUT',url,headers=headers,json=json)
		res = APIResponse(requests.put(url,headers=headers,json=json), content_type)
		return res.getData()

	def _delete(self, url, headers, json, content_type):
		res = APIResponse(requests.delete(url, headers=headers), None)
		return res.getData()

	def call(self, method, local_path, json=None, content_type='application/json;charset=utf-8', local_headers={}):
		url = self._compose_url(local_path)
		headers = self._compose_headers(local_headers)
		return self.commands[method](url, headers, json, content_type)

class APIResponse(object):

	def __init__(self, response, content_type):
		self.content_type = content_type
		self.validate(response)
		self.status = response.status_code
		if content_type == 'application/json;charset=utf-8':
			self.data = response.json()
		elif content_type in ['text/csv', 'application/pdf', 'text/xml']:
			self.data = response.content
		else:
			self.data = {'status': 'Success'}

	def validate(self, response):
		if response.status_code > 299:
			if response.status_code > 499:
				print(response.content)
			raise Exception("Error: " + str(response.status_code))
		if 'Content-Type' in response.headers and response.headers['Content-Type'] != self.content_type:
			raise Exception("Illegal content type")

	def getData(self):
		return self.data

