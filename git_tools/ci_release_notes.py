import operator
import urllib2
from urllib2 import HTTPError
import git
import re
import cookielib
import json
from git import *
import os.path
from getpass import getpass

def get_issue(server, issue_id):
	ISSUE_URL = '{0}/rest/api/2.0.alpha1/issue/{1}'.format(server, issue_id)

	req = Request(ISSUE_URL)
	try:
		result = json.loads(urlopen(req).read())
		print '{0} <{1}> {2}'.format(issue_id, '{0}/browse/{1}'.format(server, issue_id), result['fields']['summary']['value'])
	except HTTPError:
		pass

g = git.Git()
jira_server = g.config('--global', 'jira.server')
jira_user_name = g.config('--global', 'jira.username')
jira_password= g.config('--global', 'jira.password')
if jira_password == '':
    jira_password = getpass("Please enter your JIRA password: ")

# configure the rest_client
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()

COOKIEFILE = 'cookies.lwp'
if os.path.isfile(COOKIEFILE):
	cj.load(COOKIEFILE)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

AUTHN_URL = '{0}/rest/auth/1/session'.format(jira_server)
authn_request = json.dumps({'username':jira_user_name,'password':jira_password})
req = Request(AUTHN_URL, authn_request, {'Content-Type':'application/json'})
handle = urlopen(req)

#Collect the issues
repo = Repo('.')
tags = [tag for tag in reversed(sorted([tag.tag for tag in repo.tags if tag.tag is not None], key=operator.attrgetter('tagged_date')))]

tag_names = [tag.tag for tag in tags]

if 'RELEASE' in tag_names[0]:
	start=1
else:
	start=0
current_release = []

for tag in tag_names[start:]:
	if 'RELEASE' in tag:
		break
	m = re.match('JIRA-(\w+-\d+)-SIGNOFF-.*', tag)
	if m is not None:
		current_release.append(m.group(1))

for tag in set(current_release):
	get_issue(jira_server, tag)

cj.save(COOKIEFILE) 
