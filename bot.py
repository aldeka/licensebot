import requests
import json
import logging
import re
from settings_dev import license_finding_string, client_id, token

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
    r = requests.post('https://api.github.com/repos/' + owner + '/' + repo_name + '/forks',
        headers={"Authorization": "token " + token})
    logging.info(r.content)
    return r.content

#'{"id":7175710,"collaborators_url":"https://api.github.com/repos/farallon/ponyjoist/collaborators{/collaborator}","fork":true,"homepage":"","created_at":"2012-12-15T04:18:28Z","tags_url":"https://api.github.com/repos/farallon/ponyjoist/tags{/tag}","watchers_count":0,"watchers":0,"contents_url":"https://api.github.com/repos/farallon/ponyjoist/contents/{+path}","labels_url":"https://api.github.com/repos/farallon/ponyjoist/labels{/name}","network_count":0,"trees_url":"https://api.github.com/repos/farallon/ponyjoist/git/trees{/sha}","assignees_url":"https://api.github.com/repos/farallon/ponyjoist/assignees{/user}","compare_url":"https://api.github.com/repos/farallon/ponyjoist/compare/{base}...{head}","ssh_url":"git@github.com:farallon/ponyjoist.git","keys_url":"https://api.github.com/repos/farallon/ponyjoist/keys{/key_id}","milestones_url":"https://api.github.com/repos/farallon/ponyjoist/milestones{/number}","git_url":"git://github.com/farallon/ponyjoist.git","forks_count":0,"contributors_url":"https://api.github.com/repos/farallon/ponyjoist/contributors","git_commits_url":"https://api.github.com/repos/farallon/ponyjoist/git/commits{/sha}","git_refs_url":"https://api.github.com/repos/farallon/ponyjoist/git/refs{/sha}","svn_url":"https://github.com/farallon/ponyjoist","mirror_url":null,"source":{"git_url":"git://github.com/aldeka/ponyjoist.git","stargazers_url":"https://api.github.com/repos/aldeka/ponyjoist/stargazers","git_tags_url":"https://api.github.com/repos/aldeka/ponyjoist/git/tags{/sha}","updated_at":"2012-12-15T04:17:17Z","pushed_at":"2011-08-07T02:27:22Z","clone_url":"https://github.com/aldeka/ponyjoist.git","language":"Python","mirror_url":null,"issue_comment_url":"https://api.github.com/repos/aldeka/ponyjoist/issues/comments/{number}","git_commits_url":"https://api.github.com/repos/aldeka/ponyjoist/git/commits{/sha}","contributors_url":"https://api.github.com/repos/aldeka/ponyjoist/contributors","events_url":"https://api.github.com/repos/aldeka/ponyjoist/events","hooks_url":"https://api.github.com/repos/aldeka/ponyjoist/hooks","owner":{"type":"User","events_url":"https://api.github.com/users/aldeka/events{/privacy}","gists_url":"https://api.github.com/users/aldeka/gists{/gist_id}","organizations_url":"https://api.github.com/users/aldeka/orgs","url":"https://api.github.com/users/aldeka","gravatar_id":"aa452853987483f9e9e3015cf85f258d","repos_url":"https://api.github.com/users/aldeka/repos","starred_url":"https://api.github.com/users/aldeka/starred{/owner}{/repo}","followers_url":"https://api.github.com/users/aldeka/followers","following_url":"https://api.github.com/users/aldeka/following","login":"aldeka","received_events_url":"https://api.github.com/users/aldeka/received_events","avatar_url":"https://secure.gravatar.com/avatar/aa452853987483f9e9e3015cf85f258d?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png","subscriptions_url":"https://api.github.com/users/aldeka/subscriptions","id":689247},"forks":0,"svn_url":"https://github.com/aldeka/ponyjoist","watchers_count":3,"git_refs_url":"https://api.github.com/repos/aldeka/ponyjoist/git/refs{/sha}","html_url":"https://github.com/aldeka/ponyjoist","has_wiki":true,"labels_url":"https://api.github.com/repos/aldeka/ponyjoist/labels{/name}","contents_url":"https://api.github.com/repos/aldeka/ponyjoist/contents/{+path}","issue_events_url":"https://api.github.com/repos/aldeka/ponyjoist/issues/events{/number}","url":"https://api.github.com/repos/aldeka/ponyjoist","issues_url":"https://api.github.com/repos/aldeka/ponyjoist/issues{/number}","compare_url":"https://api.github.com/repos/aldeka/ponyjoist/compare/{base}...{head}","trees_url":"https://api.github.com/repos/aldeka/ponyjoist/git/trees{/sha}","forks_url":"https://api.github.com/repos/aldeka/ponyjoist/forks","milestones_url":"https://api.github.com/repos/aldeka/ponyjoist/milestones{/number}","downloads_url":"https://api.github.com/repos/aldeka/ponyjoist/downloads","merges_url":"https://api.github.com/repos/aldeka/ponyjoist/merges","commits_url":"https://api.github.com/repos/aldeka/ponyjoist/commits{/sha}","tags_url":"https://api.github.com/repos/aldeka/ponyjoist/tags{/tag}","assignees_url":"https://api.github.com/repos/aldeka/ponyjoist/assignees{/user}","keys_url":"https://api.github.com/repos/aldeka/ponyjoist/keys{/key_id}","full_name":"aldeka/ponyjoist","open_issues":0,"statuses_url":"https://api.github.com/repos/aldeka/ponyjoist/statuses/{sha}","created_at":"2011-07-20T03:51:56Z","homepage":"","size":204,"archive_url":"https://api.github.com/repos/aldeka/ponyjoist/{archive_format}{/ref}","languages_url":"https://api.github.com/repos/aldeka/ponyjoist/languages","branches_url":"https://api.github.com/repos/aldeka/ponyjoist/branches{/branch}","fork":false,"comments_url":"https://api.github.com/repos/aldeka/ponyjoist/comments{/number}","subscribers_url":"https://api.github.com/repos/aldeka/ponyjoist/subscribers","collaborators_url":"https://api.github.com/repos/aldeka/ponyjoist/collaborators{/collaborator}","name":"ponyjoist","watchers":3,"ssh_url":"git@github.com:aldeka/ponyjoist.git","has_issues":true,"forks_count":0,"pulls_url":"https://api.github.com/repos/aldeka/ponyjoist/pulls{/number}","blobs_url":"https://api.github.com/repos/aldeka/ponyjoist/git/blobs{/sha}","private":false,"id":2076048,"has_downloads":true,"open_issues_count":0,"notifications_url":"https://api.github.com/repos/aldeka/ponyjoist/notifications{?since,all,participating}","subscription_url":"https://api.github.com/repos/aldeka/ponyjoist/subscription","teams_url":"https://api.github.com/repos/aldeka/ponyjoist/teams","description":"Django app that adds a Rails-esque \'scaffold\' command that, given a model, auto-creates urls, views, and templates for basic CRUD functionality"},"open_issues_count":0,"issue_events_url":"https://api.github.com/repos/farallon/ponyjoist/issues/events{/number}","has_wiki":true,"pulls_url":"https://api.github.com/repos/farallon/ponyjoist/pulls{/number}","url":"https://api.github.com/repos/farallon/ponyjoist","master_branch":"master","subscription_url":"https://api.github.com/repos/farallon/ponyjoist/subscription","updated_at":"2012-12-15T04:18:28Z","languages_url":"https://api.github.com/repos/farallon/ponyjoist/languages","clone_url":"https://github.com/farallon/ponyjoist.git","git_tags_url":"https://api.github.com/repos/farallon/ponyjoist/git/tags{/sha}","stargazers_url":"https://api.github.com/repos/farallon/ponyjoist/stargazers","private":false,"full_name":"farallon/ponyjoist","commits_url":"https://api.github.com/repos/farallon/ponyjoist/commits{/sha}","hooks_url":"https://api.github.com/repos/farallon/ponyjoist/hooks","issue_comment_url":"https://api.github.com/repos/farallon/ponyjoist/issues/comments/{number}","comments_url":"https://api.github.com/repos/farallon/ponyjoist/comments{/number}","archive_url":"https://api.github.com/repos/farallon/ponyjoist/{archive_format}{/ref}","issues_url":"https://api.github.com/repos/farallon/ponyjoist/issues{/number}","events_url":"https://api.github.com/repos/farallon/ponyjoist/events","language":"Python","name":"ponyjoist","subscribers_url":"https://api.github.com/repos/farallon/ponyjoist/subscribers","blobs_url":"https://api.github.com/repos/farallon/ponyjoist/git/blobs{/sha}","size":204,"forks_url":"https://api.github.com/repos/farallon/ponyjoist/forks","html_url":"https://github.com/farallon/ponyjoist","teams_url":"https://api.github.com/repos/farallon/ponyjoist/teams","has_downloads":true,"open_issues":0,"description":"Django app that adds a Rails-esque \'scaffold\' command that, given a model, auto-creates urls, views, and templates for basic CRUD functionality","merges_url":"https://api.github.com/repos/farallon/ponyjoist/merges","pushed_at":"2011-08-07T02:27:22Z","statuses_url":"https://api.github.com/repos/farallon/ponyjoist/statuses/{sha}","forks":0,"parent":{"git_url":"git://github.com/aldeka/ponyjoist.git","stargazers_url":"https://api.github.com/repos/aldeka/ponyjoist/stargazers","git_tags_url":"https://api.github.com/repos/aldeka/ponyjoist/git/tags{/sha}","updated_at":"2012-12-15T04:18:28Z","pushed_at":"2011-08-07T02:27:22Z","clone_url":"https://github.com/aldeka/ponyjoist.git","language":"Python","mirror_url":null,"issue_comment_url":"https://api.github.com/repos/aldeka/ponyjoist/issues/comments/{number}","git_commits_url":"https://api.github.com/repos/aldeka/ponyjoist/git/commits{/sha}","contributors_url":"https://api.github.com/repos/aldeka/ponyjoist/contributors","events_url":"https://api.github.com/repos/aldeka/ponyjoist/events","hooks_url":"https://api.github.com/repos/aldeka/ponyjoist/hooks","owner":{"type":"User","events_url":"https://api.github.com/users/aldeka/events{/privacy}","gists_url":"https://api.github.com/users/aldeka/gists{/gist_id}","organizations_url":"https://api.github.com/users/aldeka/orgs","url":"https://api.github.com/users/aldeka","gravatar_id":"aa452853987483f9e9e3015cf85f258d","repos_url":"https://api.github.com/users/aldeka/repos","starred_url":"https://api.github.com/users/aldeka/starred{/owner}{/repo}","followers_url":"https://api.github.com/users/aldeka/followers","following_url":"https://api.github.com/users/aldeka/following","login":"aldeka","received_events_url":"https://api.github.com/users/aldeka/received_events","avatar_url":"https://secure.gravatar.com/avatar/aa452853987483f9e9e3015cf85f258d?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png","subscriptions_url":"https://api.github.com/users/aldeka/subscriptions","id":689247},"forks":1,"svn_url":"https://github.com/aldeka/ponyjoist","watchers_count":3,"git_refs_url":"https://api.github.com/repos/aldeka/ponyjoist/git/refs{/sha}","html_url":"https://github.com/aldeka/ponyjoist","has_wiki":true,"labels_url":"https://api.github.com/repos/aldeka/ponyjoist/labels{/name}","contents_url":"https://api.github.com/repos/aldeka/ponyjoist/contents/{+path}","issue_events_url":"https://api.github.com/repos/aldeka/ponyjoist/issues/events{/number}","url":"https://api.github.com/repos/aldeka/ponyjoist","issues_url":"https://api.github.com/repos/aldeka/ponyjoist/issues{/number}","compare_url":"https://api.github.com/repos/aldeka/ponyjoist/compare/{base}...{head}","trees_url":"https://api.github.com/repos/aldeka/ponyjoist/git/trees{/sha}","forks_url":"https://api.github.com/repos/aldeka/ponyjoist/forks","milestones_url":"https://api.github.com/repos/aldeka/ponyjoist/milestones{/number}","downloads_url":"https://api.github.com/repos/aldeka/ponyjoist/downloads","merges_url":"https://api.github.com/repos/aldeka/ponyjoist/merges","commits_url":"https://api.github.com/repos/aldeka/ponyjoist/commits{/sha}","tags_url":"https://api.github.com/repos/aldeka/ponyjoist/tags{/tag}","assignees_url":"https://api.github.com/repos/aldeka/ponyjoist/assignees{/user}","keys_url":"https://api.github.com/repos/aldeka/ponyjoist/keys{/key_id}","full_name":"aldeka/ponyjoist","open_issues":0,"statuses_url":"https://api.github.com/repos/aldeka/ponyjoist/statuses/{sha}","created_at":"2011-07-20T03:51:56Z","homepage":"","size":204,"archive_url":"https://api.github.com/repos/aldeka/ponyjoist/{archive_format}{/ref}","languages_url":"https://api.github.com/repos/aldeka/ponyjoist/languages","branches_url":"https://api.github.com/repos/aldeka/ponyjoist/branches{/branch}","fork":false,"comments_url":"https://api.github.com/repos/aldeka/ponyjoist/comments{/number}","subscribers_url":"https://api.github.com/repos/aldeka/ponyjoist/subscribers","collaborators_url":"https://api.github.com/repos/aldeka/ponyjoist/collaborators{/collaborator}","name":"ponyjoist","watchers":3,"ssh_url":"git@github.com:aldeka/ponyjoist.git","has_issues":true,"forks_count":1,"pulls_url":"https://api.github.com/repos/aldeka/ponyjoist/pulls{/number}","blobs_url":"https://api.github.com/repos/aldeka/ponyjoist/git/blobs{/sha}","private":false,"id":2076048,"has_downloads":true,"open_issues_count":0,"notifications_url":"https://api.github.com/repos/aldeka/ponyjoist/notifications{?since,all,participating}","subscription_url":"https://api.github.com/repos/aldeka/ponyjoist/subscription","teams_url":"https://api.github.com/repos/aldeka/ponyjoist/teams","description":"Django app that adds a Rails-esque \'scaffold\' command that, given a model, auto-creates urls, views, and templates for basic CRUD functionality"},"notifications_url":"https://api.github.com/repos/farallon/ponyjoist/notifications{?since,all,participating}","has_issues":false,"branches_url":"https://api.github.com/repos/farallon/ponyjoist/branches{/branch}","downloads_url":"https://api.github.com/repos/farallon/ponyjoist/downloads","owner":{"type":"User","events_url":"https://api.github.com/users/farallon/events{/privacy}","gists_url":"https://api.github.com/users/farallon/gists{/gist_id}","organizations_url":"https://api.github.com/users/farallon/orgs","url":"https://api.github.com/users/farallon","gravatar_id":"fbba17184dff9d224c94069d4a8f3571","repos_url":"https://api.github.com/users/farallon/repos","starred_url":"https://api.github.com/users/farallon/starred{/owner}{/repo}","followers_url":"https://api.github.com/users/farallon/followers","following_url":"https://api.github.com/users/farallon/following","login":"farallon","received_events_url":"https://api.github.com/users/farallon/received_events","avatar_url":"https://secure.gravatar.com/avatar/fbba17184dff9d224c94069d4a8f3571?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png","subscriptions_url":"https://api.github.com/users/farallon/subscriptions","id":3046166},"permissions":{"push":true,"admin":true,"pull":true}}'


def pull_request(fork):
    pass


def fork_and_add_license(repo):
    f = fork(repo['name'], repo['owner']['login'])
    pull_request(f)
    return True
