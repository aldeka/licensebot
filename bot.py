import requests
import json
import logging
import re
from settings_dev import license_finding_string, client_id

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')


def last_seen_repo():
    try:
        fin = open('last_repo_id.txt', 'r')
        print fin.readline()
        return int(fin.readline())
    except IOError:
        print 0
        return 0


def get_repos(**kwargs):
    try:
        last_seen = kwargs['last_seen']
    except KeyError:
        last_seen = last_seen_repo()
    count = 0
    pull_requests = 0

    # check rate limit
    r = requests.get('https://api.github.com/rate_limit?client_id=' + client_id)
    j = json.loads(r.content)
    try:
        logging.info("Rate limit status: " + str(j['rate']['remaining']) + " remaining")
    except KeyError:
        logging.error(str(j['message']))
        return [0, 0, 0]

    # if we still have hits, let's do this thing
    r = requests.get('https://api.github.com/repositories?since=' + str(last_seen) + '&client_id=' + client_id)
    if r.ok:
        j = json.loads(r.content)
        for repo in j:
            # is it a fork of something else?
            if not repo['fork']:
                # check for license
                # if no license, make fork and pull request
                pass
            last_seen = repo['id']
            count = count + 1
    else:
        logging.error("Connection to Github repositories endpoint failed.")

    logging.info(str(count) + " repositories scanned, ending with #" + str(last_seen))
    logging.info(str(pull_requests) + " pull request(s) made")

    #fout = open('last_repo_id.txt', 'w')
    #fout.write(str(last_seen))
    return [count, last_seen, pull_requests]


def has_license(repo):
    repo_name = repo['name']
    owner = repo['owner']['login']
    r = requests.get('https://api.github.com/repos/'+ owner + "/" + repo_name + '/contents?client_id=' + client_id)
    if r.ok:
        j = json.loads(r.content)
        for repo_file in j:
            if re.search(license_finding_string, repo_file['name']):
                return True
        # for repo_file in j:
        #     r = requests.get('http://raw.github.com/'+ owner + "/" + repo_name + '/master/' + repo_file['name'])
        #     print r.content
    return False


def fork(repo_name, owner):
    r = requests.post('https://api.github.com/repos/' + owner + '/' + repo_name + '/forks?client_id=' + client_id)
    logging.info(r.content)
    return r.content


def pull_request(fork):
    pass


def fork_and_add_license(repo):
    f = fork(repo['name'], repo['owner']['login'])
    pull_request(f)
    return True
