
import os
import sys
import git
from jinja2 import Template
from StringIO import StringIO

#list of git allowed hooks
ALLOWED_HOOKS = [ 
    'applypatch-msg',
    'pre-applypatch',
    'post-applypatch',
    'pre-commit',
    'prepare-commit-msg',
    'commit-msg',
    'post-commit',
    'pre-rebase',
    'pre-rebase',
    'post-checkout',
    'post-merge',
    'pre-receive',
    'update',
    'post-receive',
    'post-update',
    'pre-auto-gc',
    'post-rewrite',
]


#list of known projects
KNOWN_PROJECTS = [
    'CAGRID',
    'GEDI',
    'HISP',
    'BCWEB',
    'GLOBUSORGWEBSITE',
    'KOA',
    'GAL',
    'GRAPH',
    'CONTACTGRAPH',
    'GRAM',
    'GRIDFTP',
    'RIC',
    'JGLOBUS',
    'CONTACTJGLOBUS',
    'SSHEALTH',
    'CONTACTWEAVE',
    'WEAVE',
    'CABIG',
    'CONTACTCAGRID',
    'CAGRIDSECPROTO',
    'CEDPS',
    'DEVTOOL',
    'CLOUDSERVICESTEAM',
    'CUTEST',
    'DOC',
    'ESG',
    'GARS',
    'TST',
    'CONTACTGO',
    'OPS',
    'SEC',
    'GOAPRILGO',
    'GRAVI',
    'GFTPP',
    'IIS',
    'SOS',
    'GOST',
    'BIRN',
    'UX',
    'GOSTORE',
]

DEFAULT_PROJECTS = {
    'git@github.com:globusonline/globusonline-graph.git' : 'GRAPH',
    'git@github.com:globusonline/ci-dev-tools.git' : 'DEVTOOL',
}

def master_branch(branch=None):
    """Finds or sets the master branch specified in the .git/config"""
    if branch == None: #Get master branch
        try:
            master = git.Git().config('core.master')
            if master:
                return master
        except git.exc.GitCommandError:
            pass
        return "integration"
    else:
        repo = git.Repo()
        branches = filter(lambda head: head.name == branch, repo.branches)
        if len(branches) < 1:
            raise Exception("Could not find a branch with name %s" % branch)
        elif len(branches) > 1:
            raise Exception("Found more than one branch with name %s. How did you do this?" % branch)
        try:
            git.Git().config('--replace-all','core.master',branch)
        except git.exc.GitCommandError:
            raise "Failed to set master branch to %s" % branch

def find_next_signoff_tag(branch=None):
    """Finds the next available sign off tag for the current branch"""

    repo = git.Repo()
    if branch == None:
        branch = repo.active_branch.name
    tag_names = [tag.name for tag in repo.tags]
    ref_num = 0
    while True:
        ref_num += 1
        tag = "%s-SIGNOFF-%i" % (branch, ref_num)
        if not tag in tag_names:
            break

    return tag


def get_relative_file(*args):
    pwd = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(pwd, *args)

def open_default_editor(file_name):
    editor = find_editor()
    os.spawnlp(os.P_WAIT,editor, editor, file_name)

def find_editor():
    try:
        git_editor = git.Git().config('core.editor')
        if git_editor:
            return git_editor
    except git.exc.GitCommandError:
        pass
    
    try:
        env_editor = os.environ["EDITOR"]
        if env_editor:
            return env_editor
    except KeyError:
       pass
    
    return "editor"

def sign_tag(tag_name, params, template_name):
    tag = find_next_signoff_tag(params['issue_branch'])
    print tag
    #sanity check for branch name
    if not tag.startswith(tag_name):
        response = raw_input(
            "You appear to be signing a non-%s branch.  Continue? [n]" % (tag_name)
        )
        if not response.startswith(('y','Y')):
            sys.exit(-1)

    template_file = get_relative_file("jinja_templates", template_name)

    with open(template_file) as f:
       template = Template(f.read())
       source_config = StringIO(template.render(params))

    # currently git tag doesnt support templating
    # to get around this we create our own tmp file and open an editor to submit
    tmp_file = os.tmpnam()
    with open(tmp_file, 'w') as f:
       f.write(source_config.getvalue())

    open_default_editor(tmp_file)

    # tag it
    #os.execlp("git","git","tag","-s", tag)
    if os.spawnlp(os.P_WAIT,"git","git","tag","-s", tag, "-F", tmp_file) == 0:
        os.unlink(tmp_file)
    else:
        print "git tag failed - A backup of your tag message has been stored %s" % (tmp_file)
