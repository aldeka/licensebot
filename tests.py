import unittest
from bot import get_repos, has_license
import requests
import json
from settings_dev import license_finding_string, client_id


class TestGettingRepos(unittest.TestCase):
    def test_start_getting_repos(self):
        # starting from the first github repo
        result = get_repos(last_seen=0)
        self.assertEqual(result, [100, 363, 0])


class TestCheckForLicense(unittest.TestCase):
    def setUp(self):
        r = requests.get('https://api.github.com/repos/django/django?client_id=' + client_id)
        self.django_repo = json.loads(r.content)
        r = requests.get('https://api.github.com/repos/aldeka/ponyjoist?client_id=' + client_id)
        self.another_repo = json.loads(r.content)

    def test_finds_license(self):
        self.assertTrue(has_license(self.django_repo))

    def test_no_license(self):
        self.assertFalse(has_license(self.another_repo))

if __name__ == '__main__':
    unittest.main()
