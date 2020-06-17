import unittest
import os
from mock import MagicMock, patch
from codedx_api.APIs.FindingsAPI import Findings

# DO NOT UPDATE - MOCK REQUESTS DO NOT REQUIRE CREDENTIALS
api_key = "0000-0000-0000-0000"
base_url = "sample-url.codedx.com"

class FindingsAPI_test(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.findings_api = Findings(api_key, base_url)
		self.mprojs = {
			  "projects": [
			    {
			      "id": 1,
			      "name": "MockProj"
			    },
			    {
			      "id": 2,
			      "name": "ProjMock"
			    }
			  ]
			}

	@patch('requests.get')
	def test_get_finding(self, mock_get_finding):
		mock_get_finding.return_value.json.return_value = {
															"id": 5,
															"projectId": 0,
															"status": "string",
															"statusName": "string"
														}
		mock_get_finding.return_value.status_code = 200
		mock_get_finding.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding(5)
		self.assertTrue('id' in result)
		self.assertEqual(result["id"], 5)
		result = self.findings_api.get_finding(5, ["triage-time"])
		with self.assertRaises(Exception):
			self.findings_api.get_finding(None)
		with self.assertRaises(Exception):
			self.findings_api.get_finding(5, None)

	@patch('requests.get')
	def test_get_finding_description(self, mock_get_finding_description):
		mock_get_finding_description.return_value.json.return_value = {
																		  "generalDescription": {
																		    "format": "plain",
																		    "content": "string"
																		  },
																		  "instanceDescription": {
																		    "format": "plain",
																		    "content": "string"
																		  },
																		  "byResult": {
																		    "additionalProp1": {
																		      "generalDescription": {
																		        "format": "plain",
																		        "content": "string"
																		      },
																		      "instanceDescription": {
																		        "format": "plain",
																		        "content": "string"
																		      }
																		    },
																		  }
																		}
		mock_get_finding_description.return_value.status_code = 200
		mock_get_finding_description.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_description(5)
		self.assertTrue('generalDescription' in result)
		self.assertTrue('byResult' in result)
		with self.assertRaises(Exception):
			self.findings_api.get_finding_description(None)

	@patch('requests.get')
	def test_get_finding_history(self, mock_get_finding_history):
		mock_get_finding_history.return_value.json.return_value = [
																	{
																		"type": "finding-updated",
																	    "data": {
																	      "additionalProp1": {},
																	      "additionalProp2": {},
																	      "additionalProp3": {}
																	    }
																	}
																]
		mock_get_finding_history.return_value.status_code = 200
		mock_get_finding_history.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_history(5)
		self.assertTrue(isinstance(result, list))
		self.assertEqual(result[0]["type"], "finding-updated")
		with self.assertRaises(Exception):
			self.findings_api.get_finding_history(None)

	@patch('requests.get')
	@patch('requests.post')
	def test_get_finding_table(self, mock_get_finding_table, mock_projects):
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		mock_get_finding_table.return_value.json.return_value = [
																	{
																		"id": 0,
																		"projectId": 0,
																		"detectionMethod": {
																			"id": 0,
																			"name": "string",
																			"readOnly": True
																		}
																	}
																]
		mock_get_finding_table.return_value.status_code = 200
		mock_get_finding_table.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_table('MockProj')
		self.assertTrue(isinstance(result, list))
		self.assertEqual(result[0]["detectionMethod"]["id"], 0)
		result = self.findings_api.get_finding_table('MockProj', ['description'])
		result = self.findings_api.get_finding_table(proj='MockProj', query={"sort": {"by": "id", "direction": "ascending"}})
		result = self.findings_api.get_finding_table(proj='MockProj', options=["issue"], query={"sort": {"by": "id", "direction": "ascending"}})
		with self.assertRaises(Exception):
			self.findings_api.get_finding_table(5)

	@patch('requests.get')
	@patch('requests.post')
	def test_get_finding_count(self, mock_get_finding_count, mock_projects):
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		mock_get_finding_count.return_value.json.return_value = {
																	"count": 0
																}
		mock_get_finding_count.return_value.status_code = 200
		mock_get_finding_count.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_count(self.mprojs["projects"][0]["id"])
		self.assertTrue("count" in result)
		result = self.findings_api.get_finding_count(proj=self.mprojs["projects"][0]["id"], query={"sort": {"by": "id", "direction": "ascending"}})
		with self.assertRaises(Exception):
			self.findings_api.get_finding_count(-1)

	@patch('requests.get')
	@patch('requests.post')
	def test_get_finding_group_count(self, mock_get_finding_group_count, mock_projects):
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		mock_get_finding_group_count.return_value.json.return_value = [
																		{
																			"id": "string",
																			"isSynthetic": True,
																			"name": "string",
																			"rank": 0,
																			"count": 0,
																			"children": [
																				None
																		    ]
																		}
																	]
		mock_get_finding_group_count.return_value.status_code = 200
		mock_get_finding_group_count.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_group_count(self.mprojs["projects"][0]["id"])
		self.assertTrue("count" in result[0])
		result = self.findings_api.get_finding_group_count(self.mprojs["projects"][0]["id"], {"sort": {"by": "id", "direction": "ascending"}})
		with self.assertRaises(Exception):
			self.findings_api.get_finding_group_count(5)

	@patch('requests.get')
	@patch('requests.post')
	def test_get_finding_flow(self, mock_get_finding_flow, mock_projects):
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		mock_get_finding_flow.return_value.json.return_value = [
																{
																	"severity": "Low",
																	"cwe": "CWE-398: Indicator of Poor Code Quality",
																	"status": "New",
																	"rule": "SQL Injection",
																	"detected by": "FindBugs",
																	"count": 6
																}
															]
		mock_get_finding_flow.return_value.status_code = 200
		mock_get_finding_flow.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		fil = {
				"filter": {
					"detectionMethod": 1,
					"severity": "Medium"
				}
			}
		result = self.findings_api.get_finding_flow(self.mprojs["projects"][0]["id"])
		self.assertTrue("count" in result[0])
		self.assertEqual(result[0]["count"], 6)
		result = self.findings_api.get_finding_flow(self.mprojs["projects"][0]["id"], fil)
		with self.assertRaises(Exception):
			self.findings_api.get_finding_flow(-1)

	@patch('requests.get')
	def test_get_finding_file(self, mock_get_finding_file):
		projects = self.mprojs
		projects["text"] = "string"
		mock_get_finding_file.return_value.json.return_value = projects
		mock_get_finding_file.return_value.status_code = 200
		mock_get_finding_file.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		result = self.findings_api.get_finding_file(self.mprojs["projects"][0]["id"], "file")
		result = self.findings_api.get_finding_file(self.mprojs["projects"][0]["id"], 1)
		with self.assertRaises(Exception):
			self.findings_api.get_finding_file(1, [])
		with self.assertRaises(Exception):
			self.findings_api.get_finding_file(-5, 5)

if __name__ == '__main__':
    unittest.main()
