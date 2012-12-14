import requests
import json


def last_seen_repo():
    try:
        fin = open('last_repo_id.txt', 'r')
        print fin.readline()
        return int(fin.readline())
    except IOError:
        print 0
        return 0


def get_repos():
    last_seen = last_seen_repo()
    r = requests.get('https://api.github.com/repositories?since=' + str(last_seen))
    if r.ok:
        j = json.loads(r.content)
        for repo in j:
            print repo['id']
            last_seen = repo['id']
    fout = open('last_repo_id.txt', 'w')
    fout.write(str(last_seen))


def has_license(repo):
    pass


def fork(repo):
    pass


def pull_request(repo):
    pass
