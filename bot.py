import requests
import json
import logging
import re
from settings_dev import license_finding_string, client_id, token

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')


def last_seen_repo():
    '''Returns the ID number of the last repo this script has gone over.
    Right now it just reads it from a text file or returns zero.'''
    try:
        fin = open('last_repo_id.txt', 'r')
        print fin.readline()
        return int(fin.readline())
    except IOError:
        print 0
        return 0


def get_repos(**kwargs):
    '''Runs a loop that first checks if it has remaining github API requests, and if so, finds github repositories and, if appropriate, enqueues function calls which will make pull requests adding license info to them. Takes an optional argument last_seen which if given is the repo ID number it will start with.'''
    try:
        last_seen = kwargs['last_seen']
    except KeyError:
        last_seen = last_seen_repo()
    count = 0
    pull_requests = 0

    while True:
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
                    if not has_license(repo):
                        # if no license, make fork and pull request
                        # TODO: how to queue these calls?
                        fork_and_add_license(repo)
                last_seen = repo['id']
                count = count + 1
        else:
            logging.error("Connection to Github repositories endpoint failed.")
            break
            
    # some recap info after we break out of the loop

    logging.info(str(count) + " repositories scanned, ending with #" + str(last_seen))
    logging.info(str(pull_requests) + " pull request(s) made")

    fout = open('last_repo_id.txt', 'w')
    fout.write(str(last_seen))
    return [count, last_seen, pull_requests]


def has_license(repo):
    '''Given a repo dict, determine whether or not it appears to have a license already'''
    repo_name = repo['name']
    owner = repo['owner']['login']
    r = requests.get('https://api.github.com/repos/'+ owner + "/" + repo_name + '/contents?client_id=' + client_id)
    if r.ok:
        j = json.loads(r.content)
        for repo_file in j:
            if re.search(license_finding_string, repo_file['name']):
                logging.info('Found license file in repo ' + owner + '/' + repo_name)
                r = requests.get(repo_file['_links']['git'])
                if r.ok:
                    # prints text of license it thinks it found
                    print r.content
                return True
    return False


def fork(repo_name, owner):
    '''Given a repository name and a user, makes a fork of the repo on the bot's own Github account.'''
    r = requests.post('https://api.github.com/repos/' + owner + '/' + repo_name + '/forks',
        headers={"Authorization": "token " + token})
    logging.info(r.content)
    # TODO: wait five minutes
    # TODO: how do we confirm that the fork got made?
    return r.content
    
def add_license(repo_name):
    '''Given the name of a repository in the bot's own account, adds a Apache v2 license in a file called LICENSE'''
    # grr, looks like there's no way to do this via the API... :/
    # TODO: do this via the command line
    pass

def pull_request(repo_name, owner):
    '''Makes a pull request against a repository'''
    r = requests.post('https://api.github.com/repos/' + owner + '/' + repo_name + '/pulls',
        headers={
            "Authorization": "token " + token,
            "title": "Add a license file",
            "body": "Hi! I noticed your code was public, but I couldn't find any licensing information for how it could be used or reused by others. Here's a pull request that would license your code under the Apache v2 open source license. If you'd prefer to use a different license, on http://opensource.org/licenses/index.html there's a list of common ones.",
            "head": owner + ":master",
            "base": "master"
    })
    # TODO: what do errors/confirmation look like for this?
    return r.content


def fork_and_add_license(repo):
    '''Forks the repo, adds a license to the bot's fork, and then makes a pull request.
    Note that these three calls have to be done synchronously.'''
    fork(repo['name'], repo['owner']['login'])
    add_license(repo['name'])
    pull_request(repo['name'], repo['owner']['login'])
    # TODO: can we have a teardown step? can you have a pull request from a fork that no longer exists?
    return True
