import unittest
import os
from mock import MagicMock, patch
from codedx_api.CodeDxAPI import CodeDx

# DO NOT UPDATE - MOCK REQUESTS DO NOT REQUIRE CREDENTIALS
api_key = "0000-0000-0000-0000"
base_url = "https://[CODE_DX_BASE_URL].org/codedx"

class CodeDxAPI_test(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.codedx_api = CodeDx(api_key, base_url)

	def test_create_codedx(self):
		self.assertTrue(1 == 1)