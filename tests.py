import unittest
import logging
from bot import get_repos, has_license, fork
import requests
import json
from settings_dev import license_finding_string, client_id


class TestGettingRepos(unittest.TestCase):
    # def test_start_getting_repos(self):
    #     # starting from the first github repo
    #     result = get_repos(last_seen=0)
    #     self.assertEqual(result, [100, 363, 0])
    pass


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


class TestForkingRepos(unittest.TestCase):
    def setUp(self):
        r = requests.get('https://api.github.com/repos/aldeka/ponyjoist?client_id=' + client_id)
        self.repo = json.loads(r.content)

    def test_fork_repo(self):
        fork(self.repo['name'], self.repo['owner']['login'])
        success = False
        r = requests.get('https://api.github.com/users/farallon/repos?client_id=' + client_id)
        for repo in json.loads(r.content):
            print repo['full_name']
            if repo['name'] == self.repo['name']:
                success = True
                break
        self.assertTrue(success)


if __name__ == '__main__':
    # check rate limit
    r = requests.get('https://api.github.com/rate_limit?client_id=' + client_id)
    j = json.loads(r.content)
    try:
        logging.info("Rate limit status: " + str(j['rate']['remaining']) + " remaining")
    except KeyError:
        logging.error(str(j['message']))
    unittest.main()
