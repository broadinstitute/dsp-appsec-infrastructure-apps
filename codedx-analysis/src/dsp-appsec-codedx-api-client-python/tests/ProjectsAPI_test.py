import unittest
import codedx_api
from unittest.mock import MagicMock, patch
from codedx_api.APIs import ProjectsAPI

# DO NOT UPDATE - MOCK REQUESTS DO NOT REQUIRE CREDENTIALS
api_key = "0000-0000-0000-0000"
base_url = "sample-url.codedx.com"

class ProjectsAPI_test(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.proj_api = ProjectsAPI.Projects(api_key, base_url)
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
		self.musers = [
						{
							"user": {
								"id": 0,
								"type": "local",
								"name": "string",
								"principal": "string",
								"isEnabled": True,
								"isSystem": True,
								"isAdmin": True,
								"isCurrent": True
							},
							"roles": {
								"Reader": True,
								"Updater": True,
								"Creator": True,
								"Manager": True
							}
						},
						{
							"user": {
								"id": 2,
								"type": "local",
								"name": "string",
								"principal": "string",
								"isEnabled": True,
								"isSystem": True,
								"isAdmin": True,
								"isCurrent": True
							},
							"roles": {
								"Reader": True,
								"Updater": False,
								"Creator": False,
								"Manager": False
							}
						}
					]

	@patch('requests.get')
	def test_get_projects(self, mock_get_projects):
		# Creating Mock
		mock_get_projects.return_value.json.return_value = self.mprojs
		mock_get_projects.return_value.status_code = 200
		mock_get_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		# Testing...
		projs = self.proj_api.get_projects()
		self.assertTrue(isinstance(projs, dict))
		self.assertTrue('projects' in projs)

	@patch('requests.get')
	def test_update_projects(self, mock_update_projects):
		mock_update_projects.return_value.json.return_value = self.mprojs
		mock_update_projects.return_value.status_code = 200
		mock_update_projects.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api = ProjectsAPI.Projects(api_key, base_url)
		self.assertTrue(not self.proj_api.projects)
		self.proj_api.update_projects()
		self.assertEqual(len(self.mprojs['projects']), len(self.proj_api.projects))
		self.assertTrue(self.mprojs['projects'][0]['name'] in self.proj_api.projects)
		self.assertEqual(self.mprojs['projects'][0]['id'], self.proj_api.projects[self.mprojs['projects'][0]['name']])

	@patch('requests.get')
	def test_validate_name(self, mock_validate_name):
		mock_validate_name.return_value.json.return_value = self.mprojs
		mock_validate_name.return_value.status_code = 200
		mock_validate_name.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.update_projects()
		test_name = self.mprojs['projects'][0]['name']
		result = self.proj_api.validate_name(test_name)
		self.assertEqual(test_name, result)
		with self.assertRaises(Exception):
			self.proj_api.validate_name(None)
		with self.assertRaises(Exception):
			self.proj_api.validate_name("this is not a valid project name")

	@patch('requests.get')
	def test_validate_id(self, mock_validate_id):
		mock_validate_id.return_value.json.return_value = self.mprojs
		mock_validate_id.return_value.status_code = 200
		mock_validate_id.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.update_projects()
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.validate_id(test_id)
		self.assertEqual(test_id, result)
		with self.assertRaises(Exception):
			self.proj_api.validate_id(None)
		with self.assertRaises(Exception):
			self.proj_api.validate_id(-5)

	@patch('requests.get')
	def test_get_id(self, mock_get_id):
		mock_get_id.return_value.json.return_value = self.mprojs
		mock_get_id.return_value.status_code = 200
		mock_get_id.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.update_projects()
		test_name = self.mprojs['projects'][0]['name']
		result = self.proj_api.get_id(test_name)
		self.assertEqual(self.mprojs['projects'][0]['id'], result)
		with self.assertRaises(Exception):
			self.proj_api.get_id(None)
		with self.assertRaises(Exception):
			self.proj_api.get_id(0)

	@patch('requests.get')
	def test_get_name(self, mock_get_id):
		mock_get_id.return_value.json.return_value = self.mprojs
		mock_get_id.return_value.status_code = 200
		mock_get_id.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.update_projects()
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.get_name(test_id)
		self.assertEqual(self.mprojs['projects'][0]['name'], result)
		with self.assertRaises(Exception):
			self.proj_api.get_name(None)
		with self.assertRaises(Exception):
			self.proj_api.get_name("not a valid project name")

	@patch('requests.get')
	def test_process_project(self, mock_process_project):
		mock_process_project.return_value.json.return_value = self.mprojs
		mock_process_project.return_value.status_code = 200
		mock_process_project.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.update_projects()
		test_proj = self.mprojs['projects'][0]
		result = self.proj_api.process_project(test_proj['name'])
		self.assertEqual(test_proj['id'], result)
		result = self.proj_api.process_project(test_proj['id'])
		self.assertEqual(test_proj['id'], result)
		with self.assertRaises(Exception):
			self.proj_api.process_project(None)
		with self.assertRaises(Exception):
			self.proj_api.process_project(-5)
		with self.assertRaises(Exception):
			self.proj_api.process_project("This is not a valid project name")

	@patch('requests.get')
	def test_project_status(self, mock_project_status):
		mstatus = {
					"1": {
				    "type": "status",
				    "display": "New",
				    "settable": False
				  }
				}
		mock_project_status.return_value.json.return_value = mstatus
		mock_project_status.return_value.status_code = 200
		mock_project_status.return_value.headers = {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.project_status(test_id)
		self.assertTrue(result)
		self.assertEqual("status", result["1"]["type"])
		self.assertEqual(mstatus["1"]["display"], result["1"]["display"])
		with self.assertRaises(Exception):
			self.proj_api.project_status(-5)

	@patch('requests.get')
	def test_project_files(self, mock_project_files):
		mfiles = [
				  {
				    "id": 123,
				    "path": "com/foo/Bar.java"
				  },
				  {
				    "id": 124,
				    "path": "com/foo/Bang.java"
				  }
				]
		mock_project_files.return_value.json.return_value = mfiles
		mock_project_files.return_value.status_code = 200
		mock_project_files.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.project_files(test_id)
		self.assertTrue(isinstance(result, list))
		self.assertEqual("com/foo/Bar.java", result[0]["path"])
		with self.assertRaises(Exception):
			self.proj_api.project_files(-5)

	@patch('requests.get')
	def test_project_roles(self, mock_project_roles):
		mock_project_roles.return_value.json.return_value = self.musers
		mock_project_roles.return_value.status_code = 200
		mock_project_roles.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.project_roles(test_id)
		self.assertTrue(isinstance(result, list))
		self.assertTrue("user" in result[0])
		self.assertTrue("roles" in result[0])
		self.assertTrue(result[0]["roles"]["Reader"])
		with self.assertRaises(Exception):
			self.proj_api.project_roles(-5)

	@patch('requests.get')
	def test_project_user(self, mock_project_user):
		mock_project_user.return_value.json.return_value = self.musers[0]
		mock_project_user.return_value.status_code = 200
		mock_project_user.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_id = self.mprojs['projects'][0]['id']
		result = self.proj_api.project_user(test_id, 0)
		self.assertTrue("user" in result)
		self.assertTrue("roles" in result)
		# create user id API to check for users
		# with self.assertRaises(Exception):
		#	self.proj_api.project_user(test_id, -5)

	@patch('requests.put')
	def test_create_project(self, mock_create_project):
		mres = {
				  "id": 49,
				  "name": "CreateTest"
				}
		mock_create_project.return_value.json.return_value = mres
		mock_create_project.return_value.status_code = 200
		mock_create_project.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		testName = "CreateTest"
		result = self.proj_api.create_project(testName)
		self.assertEqual(result["id"], 49)
		self.assertEqual(result["name"], testName)

	@patch('requests.delete')
	def test_delete_project(self, mock_delete_project):
		mock_delete_project.return_value.status_code = 204
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_name = "ProjMock"
		result = self.proj_api.delete_project(test_name)
		self.assertEqual(result["status"], "Success")
		self.assertTrue(test_name not in self.proj_api.projects)

	@patch('requests.put')
	def test_update_project(self, mock_update_project):
		mock_update_project.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_name = "UpdateTest"
		test_id = 1
		result = self.proj_api.update_project(test_id, new=test_name)
		self.assertEqual(result["status"], "Success")
		self.assertEqual(test_id, self.proj_api.projects[test_name])

	@patch('requests.put')
	@patch('requests.get')
	def test_update_user_roles(self, mock_update_user_roles, mock_user_roles):
		mock_update_user_roles.return_value.status_code = 200
		mock_user_roles.return_value.json.return_value = self.musers[0]
		mock_user_roles.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		result = self.proj_api.update_user_roles("MockProj", 0, ["Creator", "Manager"], False)
		self.assertEqual(result["status"], "Success")
		result = self.proj_api.update_user_roles("MockProj", 0, ["Creator", "Manager"], True)
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.proj_api.update_user_roles("Not a valid project", 0, ["Creator", "Manager"], False)
		with self.assertRaises(Exception):
			self.proj_api.update_user_roles("Not a valid project", 0, ["NotRealRole"], False)
		# add user checks
		#with self.assertRaises(Exception):
		#	self.proj_api.update_user_roles("MockProj", -4, ["Reader"], False)


	@patch('requests.put')
	@patch('requests.get')
	def test_add_user_roles(self, mock_add_user_roles, mock_user_roles):
		mock_add_user_roles.return_value.status_code = 200
		mock_user_roles.return_value.json.return_value = self.musers[0]
		mock_user_roles.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		result = self.proj_api.add_user_roles("MockProj", 0, ["Reader", "Updater"])
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.proj_api.add_user_roles("Not a valid project", 0, ["Creator", "Manager"])
		with self.assertRaises(Exception):
			self.proj_api.add_user_roles("MockProj", 0, ["NotRealRole"])
		# add user checks
		#with self.assertRaises(Exception):
		#	self.proj_api.add_user_roles("MockProj", -4, ["Reader"])

	@patch('requests.put')
	@patch('requests.get')
	def test_rem_user_roles(self, mock_rem_user_roles, mock_user_roles):
		mock_rem_user_roles.return_value.status_code = 200
		mock_user_roles.return_value.json.return_value = self.musers[0]
		mock_user_roles.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		result = self.proj_api.add_user_roles("MockProj", 0, ["Creator", "Manager"])
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.proj_api.rem_user_roles("Not a valid project", 0, ["Creator", "Manager"])
		with self.assertRaises(Exception):
			self.proj_api.rem_user_roles("MockProj", 0, ["NotRealRole"])
		# add user checks
		#with self.assertRaises(Exception):
		#	self.proj_api.rem_user_roles("MockProj", -4, ["Reader"])

	@patch('requests.put')
	@patch('requests.get')
	def test_add_user_role(self, mock_add_user_role, mock_user_roles):
		mock_add_user_role.return_value.status_code = 200
		mock_user_roles.return_value.json.return_value = self.musers[0]
		mock_user_roles.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		result = self.proj_api.add_user_role("MockProj", 0, "Reader")
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.proj_api.add_user_role("Not a valid project", 0, "Creator")
		with self.assertRaises(Exception):
			self.proj_api.add_user_role("MockProj", 0, "NotRealRole")
		# add user checks
		#with self.assertRaises(Exception):
		#	self.proj_api.add_user_role("MockProj", -4, "Reader")

	@patch('requests.put')
	@patch('requests.get')
	def test_rem_user_role(self, mock_rem_user_role, mock_user_roles):
		mock_rem_user_role.return_value.status_code = 200
		mock_user_roles.return_value.json.return_value = self.musers[0]
		mock_user_roles.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		result = self.proj_api.rem_user_role("MockProj", 0, "Manager")
		self.assertEqual(result["status"], "Success")
		with self.assertRaises(Exception):
			self.proj_api.rem_user_role("Not a valid project", 0, "Creator")
		with self.assertRaises(Exception):
			self.proj_api.rem_user_role("MockProj", 0, "NotRealRole")
		# add user checks
		#with self.assertRaises(Exception):
		#	self.proj_api.add_user_role("MockProj", -4, "Reader")

	@patch('requests.post')
	def test_query(self, mock_query_base):
		mock_query_base.return_value.json.return_value = [
															{
																"id": 12,
																"name": "The first webgoat project",
																"parentId": None,
																"hierarchyIds": [],
																"latestCompleteAnalysis": {
																	"id": 3,
																	"projectId": 12,
																	"state": "complete",
																	"createdBy": {
																		"id": 1,
																		"name": "admin"
																	},
																	"creationTime": "2018-01-17T11:33:42.000-05:00",
																	"startTime": "2018-01-17T11:33:42.000-05:00",
																	"endTime": "2018-01-17T11:33:42.000-05:00"
																},
																"metadata": [
																	{
																		"id": 1,
																		"name": "Project Owner",
																		"value": "Jim"
																	},
																	{
																		"id": 5,
																		"name": "Impact",
																		"value": "Medium"
																	},
																	{
																		"id": 7,
																		"name": "My Tags Field",
																		"value": "hello world"
																	}
																]
															}
														]
		mock_query_base.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		mock_query_base.return_value.status_code = 200
		result = self.proj_api.query_base('/api/projects/query', "webgoat", None, None, None, None)
		self.assertEqual(result[0]["name"], "The first webgoat project")
		result = self.proj_api.query_base('/api/projects/query', "webgoat", None, None, 10, 100)
		self.assertEqual(result[0]["name"], "The first webgoat project")
		result = self.proj_api.query("webgoat", None, None, 10, 100)
		self.assertEqual(result[0]["name"], "The first webgoat project")
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, None, None, None, None)
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', 5, None, None, None, None)
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, None, None, 10, None)
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, None, None, -2, 20)
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, None, None, 2, -20)
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, None, "bad parentid", None, None)	
		with self.assertRaises(Exception):
			self.proj_api.query_base('/api/projects/query', None, 5, None, None, None)

	@patch('requests.post')
	def test_query_count(self, mock_query_count):
		mock_query_count.return_value.json.return_value = 13
		mock_query_count.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		mock_query_count.return_value.status_code = 200
		result = self.proj_api.query_count("webgoat", None, None)
		self.assertEqual(result, 13)

	@patch('requests.post')
	def test_file_paths(self, mock_file_paths):
		mock_file_paths.return_value.json.return_value = {
															"C:/code/myproject/src/main/java/com/foo/Bar.java": {
																"id": 1234,
																"path": "somewhere/src/main/java/com/foo/Bar.java"
															},
															"DatabaseUtilities.java": {
																"id": 789,
																"path": "somewhere/src/main/java/com/foo/DatabaseUtilities.java"
															}
														}
		mock_file_paths.return_value.headers["Content-Type"] = 'application/json;charset=utf-8'
		mock_file_paths.return_value.status_code = 200
		self.proj_api.projects = {'MockProj': 1, 'ProjMock': 2}
		test_files = [
					    "C:/code/myproject/src/main/java/com/foo/Bar.java",
					    "DatabaseUtilities.java"
					  ]
		result = self.proj_api.file_paths(1, test_files)
		self.assertTrue(test_files[0] in result)
		with self.assertRaises(Exception):
			result = self.proj_api.file_paths(-1, test_files)
		with self.assertRaises(Exception):
			result = self.proj_api.file_paths(1, {"files"})

if __name__ == '__main__':
    unittest.main()