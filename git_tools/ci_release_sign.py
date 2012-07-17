
import git
from jinja2 import Template
from git_common import sign_tag

if __name__ == "__main__":

    params = {}
    params['issue_branch'] =  git.Repo().active_branch.name
    params['merge_branch'] = "production"  # hardcoded as we are always merging into production

    sign_tag('RELEASE', params, "release_sign_template.txt")
