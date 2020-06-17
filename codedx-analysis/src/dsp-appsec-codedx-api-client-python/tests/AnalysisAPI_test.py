import unittest
import os
from mock import MagicMock, patch
from codedx_api.APIs.AnalysisAPI import Analysis

# DO NOT UPDATE - MOCK REQUESTS DO NOT REQUIRE CREDENTIALS
api_key = "0000-0000-0000-0000"
base_url = "https://[CODE_DX_BASE_URL].org/codedx"

class AnalysisAPI_test(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.analysis_api = Analysis(api_key, base_url)
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
		self.manalysis = {
							"prepId": "string",
							"verificationErrors": [
								"string"
							],
							"scmSetup": {
								"scmInfo": {
									"repoType": "string",
									"url": "string",
									"rev": {
										"revType": "branch",
										"revName": "string",
										"revDetail": "string"
									}
								},
								"inputId": "myInputId",
								"setupJobId": "string"
							}
						}

	@patch('requests.get')
	@patch('requests.post')
	def test_create_analysis(self, mock_create_analysis, mock_projects):
		mock_create_analysis.return_value.json.return_value = self.manalysis
		mock_create_analysis.return_value.status_code = 200
		mock_create_analysis.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		test_proj = self.mprojs['projects'][0]['name']
		result = self.analysis_api.create_analysis(test_proj)
		self.assertTrue('prepId' in result)
		self.assertTrue(isinstance(result['prepId'], str))
		self.assertEqual(self.manalysis["scmSetup"]["inputId"], result["scmSetup"]["inputId"])
		with self.assertRaises(Exception):
			self.analysis_api.create_analysis(-1)

	@patch('requests.get')
	def test_get_prep(self, mock_get_prep):
		mock_get_prep.return_value.json.return_value = {
															"inputIds": [
																"myInputId"
															],
															"verificationErrors": [
																"string"
															]
														}
		mock_get_prep.return_value.status_code = 200
		mock_get_prep.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		result = self.analysis_api.get_prep(self.manalysis["prepId"])
		self.assertTrue(isinstance(result["inputIds"], list))

	@patch('requests.post')
	def test_upload_analysis(self, mock_upload_analysis):
		mock_upload_analysis.return_value.json.return_value = {
																"jobId": "myJobString",
																"inputId": "string",
																"size": 0
															}
		mock_upload_analysis.return_value.status_code = 202
		mock_upload_analysis.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		test_prep_id = "myTestPrep"
		test_file_name = os.path.join(os.path.dirname(__file__), 'testdata.xml')
		result = self.analysis_api.upload_analysis(test_prep_id, test_file_name)
		self.assertEqual(result["jobId"], "myJobString")
		with self.assertRaises(Exception):
			self.analysis_api.upload_analysis(-5, test_file_name)
		with self.assertRaises(Exception):
			self.analysis_api.upload_analysis(test_prep_id, "Not a valid file name")
		with self.assertRaises(Exception):
			self.analysis_api.upload_analysis(test_prep_id, "not_valid_ext.html")

	@patch('requests.post')
	def test_run_analysis(self, mock_run_analysis):
		mock_run_analysis.return_value.json.return_value = {
															"analysisId": 0,
															"jobId": "runningAnalysis"
														}
		mock_run_analysis.return_value.status_code = 202
		mock_run_analysis.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		test_prep_id = "myTestPrep"
		result = self.analysis_api.run_analysis(test_prep_id)
		self.assertEqual(result["jobId"], "runningAnalysis")
		self.assertEqual(result["analysisId"], 0)
		with self.assertRaises(Exception):
			self.analysis_api.run_analysis(-5)

	@patch('requests.get')
	def test_get_input_metadata(self, mock_get_input_metadata):
		mock_get_input_metadata.return_value.json.return_value = {
																  "tags": [
																    {
																      "source": "string",
																      "binary": "string",
																      "buildMeta": "string",
																      "toolOutput": "string",
																      "toolInput": "string",
																      "id": "string",
																      "enabled": True,
																      "enabledReason": "string"
																    }
																  ],
																  "scmInfo": {
																    "repoType": "string",
																    "url": "string",
																    "rev": {
																      "revType": "branch",
																      "revName": "string",
																      "revDetail": "string"
																    }
																  },
																  "warnings": [
																    "string"
																  ],
																  "errors": [
																    "string"
																  ]
																}
		mock_get_input_metadata.return_value.status_code = 200
		mock_get_input_metadata.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		result = self.analysis_api.get_input_metadata('1234', 'TEST')
		self.assertTrue("tags" in result)
		self.assertEqual(len(result["warnings"]), 1)
		with self.assertRaises(Exception):
			self.analysis_api.get_input_metadata(1, 'TEST')
		with self.assertRaises(Exception):
			self.analysis_api.get_input_metadata('1234', 2)

	@patch('requests.delete')
	def test_delete_input(self, mock_delete_input):
		mock_delete_input.return_value.status_code = 200
		result = self.analysis_api.delete_input('1234', 'TEST')
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.analysis_api.delete_input(1, 'TEST')
		with self.assertRaises(Exception):
			self.analysis_api.delete_input('1234', 2)

	@patch('requests.delete')
	def test_delete_pending(self, mock_delete_pending):
		mock_delete_pending.return_value.status_code = 200
		result = self.analysis_api.delete_pending('1234', 'TEST')
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.analysis_api.delete_pending(1, 'TEST')
		with self.assertRaises(Exception):
			self.analysis_api.delete_pending('1234', 2)

	@patch('requests.put')
	def test_toggle_display_tag(self, mock_toggle_display_tag):
		mock_toggle_display_tag.return_value.json.return_value = {
																  "tags": [
																    {
																      "source": "string",
																      "binary": "string",
																      "buildMeta": "string",
																      "toolOutput": "string",
																      "toolInput": "string",
																      "id": "string",
																      "enabled": True,
																      "enabledReason": "string"
																    }
																  ],
																  "scmInfo": {
																    "repoType": "string",
																    "url": "string",
																    "rev": {
																      "revType": "branch",
																      "revName": "string",
																      "revDetail": "string"
																    }
																  },
																  "warnings": [
																    "string"
																  ],
																  "errors": [
																    "string"
																  ]
																}
		mock_toggle_display_tag.return_value.status_code = 200
		mock_toggle_display_tag.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		result = self.analysis_api.toggle_display_tag('1234', 'inputId', 'tagID', True)
		self.assertTrue("tags" in result)
		self.assertEqual(len(result["warnings"]), 1)
		with self.assertRaises(Exception):
			self.analysis_api.toggle_display_tag(1234, 'inputId', 'tagID', True)
		with self.assertRaises(Exception):
			self.analysis_api.toggle_display_tag('1234', 1234, 'tagID', True)
		with self.assertRaises(Exception):
			self.analysis_api.toggle_display_tag('1234', 'inputId', 1234, True)
		with self.assertRaises(Exception):
			self.analysis_api.toggle_display_tag('1234', 'inputId', 'tagID', None)						

	@patch('requests.put')
	def test_enable_display_tag(self, mock_enable_display_tag):
		mock_enable_display_tag.return_value.json.return_value = {
																  "tags": [
																    {
																      "source": "string",
																      "binary": "string",
																      "buildMeta": "string",
																      "toolOutput": "string",
																      "toolInput": "string",
																      "id": "string",
																      "enabled": True,
																      "enabledReason": "string"
																    }
																  ],
																  "scmInfo": {
																    "repoType": "string",
																    "url": "string",
																    "rev": {
																      "revType": "branch",
																      "revName": "string",
																      "revDetail": "string"
																    }
																  },
																  "warnings": [
																    "string"
																  ],
																  "errors": [
																    "string"
																  ]
																}
		mock_enable_display_tag.return_value.status_code = 200
		mock_enable_display_tag.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		result = self.analysis_api.enable_display_tag('1234', 'inputId', 'tagID')
		self.assertTrue("tags" in result)
		self.assertTrue(result["tags"][0]["enabled"])
		self.assertEqual(len(result["warnings"]), 1)
		with self.assertRaises(Exception):
			self.analysis_api.enable_display_tag(1234, 'inputId', 'tagID')
		with self.assertRaises(Exception):
			self.analysis_api.enable_display_tag('1234', 1234, 'tagID')
		with self.assertRaises(Exception):
			self.analysis_api.enable_display_tag('1234', 'inputId', 1234)	

	@patch('requests.put')
	def test_disable_display_tag(self, mock_disable_display_tag):
		mock_disable_display_tag.return_value.json.return_value = {
																  "tags": [
																    {
																      "source": "string",
																      "binary": "string",
																      "buildMeta": "string",
																      "toolOutput": "string",
																      "toolInput": "string",
																      "id": "string",
																      "enabled": False,
																      "enabledReason": "string"
																    }
																  ],
																  "scmInfo": {
																    "repoType": "string",
																    "url": "string",
																    "rev": {
																      "revType": "branch",
																      "revName": "string",
																      "revDetail": "string"
																    }
																  },
																  "warnings": [
																    "string"
																  ],
																  "errors": [
																    "string"
																  ]
																}
		mock_disable_display_tag.return_value.status_code = 200
		mock_disable_display_tag.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		result = self.analysis_api.disable_display_tag('1234', 'inputId', 'tagID')
		self.assertTrue("tags" in result)
		self.assertFalse(result["tags"][0]["enabled"])
		self.assertEqual(len(result["warnings"]), 1)
		with self.assertRaises(Exception):
			self.analysis_api.disable_display_tag(1234, 'inputId', 'tagID')
		with self.assertRaises(Exception):
			self.analysis_api.disable_display_tag('1234', 1234, 'tagID')
		with self.assertRaises(Exception):
			self.analysis_api.disable_display_tag('1234', 'inputId', 1234)	

	@patch('requests.get')
	def test_get_all_analysis(self, mock_get_all_analysis):
		mock_get_all_analysis.return_value.json.return_value = [{
																"id": 0,
																"projectId": 3,
																"state": "string",
																"createdBy": {
																	"id": 0,
																	"name": "string"
																},
																"creationTime": "string",
																"startTime": "string",
																"endTime": "string",
																"name": "string"
															}]
		mock_get_all_analysis.return_value.status_code = 200
		mock_get_all_analysis.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.analysis_api.projects_api.projects = {'MockProj': 3}
		result = self.analysis_api.get_all_analysis('MockProj')
		self.assertEqual(result[0]["id"], 0)
		self.assertEqual(result[0]["projectId"], 3)
		with self.assertRaises(Exception):
			self.analysis_api.get_all_analysis('Not a Project')

	@patch('requests.get')
	def test_get_analysis(self, mock_get_analysis):
		mock_get_analysis.return_value.json.return_value = {
																"id": 0,
																"projectId": 3,
																"state": "string",
																"createdBy": {
																	"id": 0,
																	"name": "string"
																},
																"creationTime": "string",
																"startTime": "string",
																"endTime": "string",
																"name": "string"
															}
		mock_get_analysis.return_value.status_code = 200
		mock_get_analysis.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.analysis_api.projects_api.projects = {'MockProj': 3}
		result = self.analysis_api.get_analysis('MockProj', 0)
		self.assertEqual(result["id"], 0)
		self.assertEqual(result["projectId"], 3)
		with self.assertRaises(Exception):
			self.analysis_api.get_analysis('Not a Project', 2)
		with self.assertRaises(Exception):
			self.analysis_api.get_analysis('MockProj', 'TEST')

	@patch('requests.get')
	@patch('requests.put')
	def test_name_analysis(self, mock_name_analysis, mock_projects):
		mock_projects.return_value.json.return_value = self.mprojs
		mock_projects.return_value.status_code = 200
		mock_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		mock_name_analysis.return_value.status_code = 204
		self.analysis_api.projects_api.projects = {'MockProj': 3}
		result = self.analysis_api.name_analysis('MockProj', 1, 'NewName')
		print(result)
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.analysis_api.name_analysis('Not a Project', 1, 'NewName')
		with self.assertRaises(Exception):
			self.analysis_api.name_analysis('MockProj', None, 'NewName')
		with self.assertRaises(Exception):
			self.analysis_api.name_analysis('MockProj', 1, None)	

if __name__ == '__main__':
    unittest.main()

