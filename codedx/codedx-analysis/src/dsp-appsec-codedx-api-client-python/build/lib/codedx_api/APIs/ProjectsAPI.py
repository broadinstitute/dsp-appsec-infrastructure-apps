from codedx_api.APIs.BaseAPIClient import BaseAPIClient
import json
import re

# Projects Client for Code DX Projects API
class Projects(BaseAPIClient):
	
	def __init__(self, base, api_key, verbose = False):
		""" Creates an API Client for Code DX Projects API
				base: String representing base url from Code DX
				api_key: String representing API key from Code DX
				verbose: Boolean - not supported yet

		"""
		super().__init__(base, api_key, verbose)
		self.roles = ['Reader', 'Updater', 'Creator', 'Manager']
		self.projects = {}

	def get_projects(self):
		""" Lists all projects. Updates Projects() instance.
			Returns Dict[name] = id
		"""
		local_url = '/api/projects'
		res = self.call("GET", local_url)
		return res

	def update_projects(self):
		res = self.get_projects()
		if 'projects' in res:
			for row in res['projects']:
				self.projects[row['name']] = row['id']

	def print_projects(self):
		""" Prints the current list of projects. """
		print("Project (ID)\n==============")
		for name in sorted(self.projects.keys()):
			print("%s (%d)" % (name, self.projects[name]))

	def validate_name(self, name):
		""" Returns a valid project name. """
		if len(self.projects) == 0:
			self.update_projects()
		if name not in self.projects:
			raise Exception("Not a valid project name.")
		return name

	def validate_id(self, pid):
		""" Returns a valid project id. """
		if len(self.projects) == 0:
			self.update_projects()
		if pid not in self.projects.values():
			raise Exception("Not a valid project id.")
		return pid

	def get_id(self, name):
		""" Given a project name, returns a valid project id. """
		self.validate_name(name)
		return self.projects[name]

	def get_name(self, pid):
		""" Given a project name, returns a valid project id. """
		self.validate_id(pid)
		for key in self.projects:
			if pid == self.projects[key]:
				return key
		raise Exception("Not a valid project id.")

	def process_project(self, proj):
		""" Given a project name or id, returns a valid project id. """
		if isinstance(proj, str):
			return self.get_id(proj)
		elif isinstance(proj, int):
			return self.validate_id(proj)
		raise Exception("Invalid Input.")

	def project_status(self, proj):
		""" Provides information on all valid triage statuses for a project.
			Accepts either a project name or id.
		"""
		pid = self.process_project(proj)
		local_url = '/api/projects/%d/statuses' % pid
		res = self.call("GET", local_url)
		return res

	def project_files(self, proj):
		""" Provides a list of files for a project.
			Accepts either a project name or id.
		"""
		pid = self.process_project(proj)
		local_url = '/api/projects/%d/files' % pid
		res = self.call("GET", local_url)
		return res

	def project_roles(self, proj):
		""" Provides a list of all User roles.
			Accepts either a project name or id.
		"""
		pid = self.process_project(proj)
		local_url = '/api/projects/%d/user-roles' % pid
		res = self.call("GET", local_url)
		return res

	def project_user(self, proj, uid):
		""" Provides a User Role for a given user.
			Accepts either a project name or id. Requires a user id.
		"""
		pid = self.process_project(proj)
		local_url = '/api/projects/%d/user-roles/user/%d' % (pid, uid)
		res = self.call("GET", local_url)
		return res

	def create_project(self, name):
		""" Creates a project.
			Accepts project name.
		"""
		if name in self.projects:
			raise Exception("Project name already exists.")
		if re.search('[a-zA-Z]', name) is None:
			raise Exception("Did not input a valid name.")
		local_url = '/api/projects'
		params = {"name": name}
		res = self.call("PUT", local_url, params)
		self.projects[res['name']] = res['id']
		return res

	def delete_project(self, proj):
		""" Deletes a project.
			Accepts either a project name or a project id.
		"""
		pid = self.process_project(proj)
		local_url = '/api/projects/%d' % pid
		res = self.call("DELETE", local_url)
		if res["status"] == "Success":
			name = self.get_name(pid)
			del self.projects[name]
		return res

	def update_project(self, proj, new = None, parentId = None):
		""" Update a project by changing its name or parent.
			Accepts either a project name or a project id and parameters to update.
		"""
		pid = self.process_project(proj)
		old_name = self.get_name(pid)
		local_url = '/api/projects/%d' % pid
		params = {}
		if parentId is None and new is None:
			raise Exception("No input given to update.")
		if parentId is not None:
			params['parentId'] = parentId
		if new is not None:
			params['name'] = new
		res = self.call("PUT", local_url, json=params, content_type=None)
		if res["status"] == "Success" and new is not None:
			self.projects[new] = pid
			del self.projects[old_name]
		return res

	# might want to move into codedx wrapper....
	def update_user_roles(self, proj, uid, roles, add):
		""" Update a user by adding or removing roles.
			Accepts a project name or id, a user id, and a list of roles to add.
			A user can have reader, updater, creator, and manager roles.	
		"""
		pid = self.process_project(proj)
		user_roles = self.project_user(pid, uid)['roles']
		for role in roles:
			if role in self.roles:
				user_roles[role] = add
			else:
				raise Exception("Given role is not an accepted role.")
		local_url = '/api/projects/%d/user-roles/user/%d' % (pid, uid)
		res = self.call("PUT", local_url, json=user_roles, content_type=None)
		return res

	def add_user_roles(self, proj, uid, roles):
		""" Update a user by adding roles.
			Accepts a project name or id, a user id, and a list of roles to add.
			A user can have reader, updater, creator, and manager roles.	
		"""
		res = self.update_user_roles(proj, uid, roles, True)
		return res
		

	def rem_user_roles(self, proj, uid, roles):
		""" Update a user by removing roles.
			Accepts a project name or id, a user id, and a list of roles to remove.
			A user can have reader, updater, creator, and manager roles.	
		"""
		res = self.update_user_roles(proj, uid, roles, False)
		return res

	def add_user_role(self, proj, uid, role):
		""" Update a user by adding a role.
			Accepts a project name or id, a user id, and a role to add.
			A user can have reader, updater, creator, and manager roles.	
		"""
		res = self.update_user_roles(proj, uid, [role], True)
		return res

	def rem_user_role(self, proj, uid, role):
		""" Update a user by removing a role.
			Accepts a project name or id, a user id, and a role to add.
			A user can have reader, updater, creator, and manager roles.	
		"""		
		res = self.update_user_roles(proj, uid, [role], False)
		return res


	def query_base(self, url, name, metadata, parentId, offset, limit):
		""" Gets the number of projects or a list of projects which match some filter/query criteria, and which you are allowed to view.
			Accepts at least one filter:
				- name <String>: Each matching project should contain the given text in their name
				- metadata <Dict>: A dictionary containing project metadata fields and their respective search criteria
				- parentId <Int> or None: If int, each matching project should be a direct child of the parent. If null, each matching project should be top level
			Limit <Int>: The maximum number or results
			Offest <Int>: An offset to the limit. Specifying and offset with a limit is an error.
		"""
		if name is None and metadata is None and parentId is None:
			raise Exception("Need a filter to query.")
		if offset is not None and limit is None:
			raise Exception("Cannot specify an offset without a limit.")
		params = {}
		filters = {}
		if name is not None and self.type_check(name, str, "Project name") : filters['name'] = name 
		if metadata is not None and self.type_check(metadata, dict, "Metadata") : filters['metadata'] = metadata 
		# parent Id can be an integer or null
		if parentId is not False and (parentId is None or self.type_check(parentId, int, "Parent Id")) : filters['parentId'] = parentId 
		params['filter'] = filters
		if offset is not None and self.type_check(offset, int, "Offset") : params['offset'] = offset 
		if limit is not None and self.type_check(limit, int, "Limit") : params['limit'] = limit 
		if (offset or limit) and (offset < 0 or limit < 1):
			raise Exception("Limit and offset must be a positive integer")
		res = self.call("POST", url, json=params)
		return res

	def query(self, name=None, metadata=None, parentId=False, offset=None, limit=None):
		""" Gets a list of projects which match some filter/query criteria, and which you are allowed to view.
			Accepts at least one filter:
				- name <String>: Each matching project should contain the given text in their name
				- metadata <Dict>: A dictionary containing project metadata fields and their respective search criteria
				- parentId <Int> or None: If int, each matching project should be a direct child of the parent. If null, each matching project should be top level
			Limit <Int>: The maximum number or results
			Offest <Int>: An offset to the limit. Specifying and offset with a limit is an error.
		"""
		local_url = '/api/projects/query'
		res = self.query_base(local_url, name, metadata, parentId, offset, limit)
		return res

	def query_count(self, name=None, metadata=None, parentId=False):
		""" Gets the number of projects which match some filter/query criteria, and which you are allowed to view.
			Accepts at least one filter:
				- name <String>: Each matching project should contain the given text in their name
				- metadata <Dict>: A dictionary containing project metadata fields and their respective search criteria
				- parentId <Int> or None: If int, each matching project should be a direct child of the parent. If null, each matching project should be top level
			Limit and offset are accepted but ignored.
		"""
		offset = None
		limit = None
		local_url = '/api/projects/query/count'
		res = self.query_base(local_url, name, metadata, parentId, offset, limit)
		return res

	def file_paths(self, proj, files):
		""" Provides source path mappings for a project.
			Accepts a list of strings representing files.
		"""
		pid = self.process_project(proj)
		self.type_check(files, list, "Files ")
		params = {"files": files}
		url = '/api/projects/%d/files/mappings' % pid
		res = self.call("POST", url, json=params)
		return res
