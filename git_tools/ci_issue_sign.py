
import git
import sys
from jinja2 import Template
from git_common import sign_tag

import git_common

if __name__ == "__main__":

    params = {}
    # TODO: Is this correct? Should you be able to specify the branch?
    params['issue_branch'] =  git.Repo().active_branch.name
    params['merge_branch'] = git_common.master_branch()
    if len(sys.argv) > 1:
        params['merge_branch'] = sys.argv[1]
        if params['merge_branch'] not in [b.name for b in git.Repo().branches]:
            print "Branch %s does not exist. Have you checked it out?" % params['merge_branch']
            sys.exit(-1)
    if params['issue_branch'].lower() == params['merge_branch'].lower():
        print "You cannot merge an issue branch (%s) into itself" % params['issue_branch']
        sys.exit(-1)

    sign_tag('JIRA', params, "issue_sign_template.txt")
