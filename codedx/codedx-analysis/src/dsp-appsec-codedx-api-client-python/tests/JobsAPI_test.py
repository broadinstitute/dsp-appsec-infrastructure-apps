import unittest
from mock import MagicMock, patch
from codedx_api.APIs import JobsAPI

# DO NOT UPDATE - MOCK REQUESTS DO NOT REQUIRE CREDENTIALS
api_key = "0000-0000-0000-0000"
base_url = "sample-url.codedx.com"

class JobsAPI_test(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.job_api = JobsAPI.Jobs(api_key, base_url)


	@patch('requests.get')
	def test_job_status(self, mock_job_status):
		mock_job_status.return_value.json.return_value =  {
														  "jobId": "string",
														  "status": "queued"
														}
		mock_job_status.return_value.status_code = 200
		mock_job_status.return_value.headers= {"Content-Type": 'application/json;charset=utf-8'}
		test_job = "string"
		result = self.job_api.job_status(test_job)
		self.assertTrue('jobId' in result)
		self.assertEqual(result["jobId"], test_job)
		self.assertTrue("status" in result)
		with self.assertRaises(Exception):
			self.job_api.job_status(-1)

	@patch('requests.get')
	def test_job_result(self, mock_job_result):
		mock_job_result.return_value.json.return_value =  "\"Project Hierarchy\",\"ID\",\"First Seen\"\n\"CRSP Portal\",\"8469\",\"2019-07-24T18:13:28Z\""
		mock_job_result.return_value.status_code = 200
		mock_job_result.return_value.headers= {"Content-Type": 'text/csv'}
		test_job = "string"
		result = self.job_api.job_result(test_job, 'text/csv')
		self.assertTrue(result is not None)
		with self.assertRaises(Exception):
			test_job = "string"
			result = self.job_api.job_result(test_job)

if __name__ == '__main__':
    unittest.main()