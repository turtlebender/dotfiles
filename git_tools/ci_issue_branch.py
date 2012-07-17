
import os
import sys
import re
import git

import git_common
from git_common import KNOWN_PROJECTS
from git_common import DEFAULT_PROJECTS

if __name__ == "__main__":
    try:
        issue = sys.argv[1]
    except:
        print "You must include an issue id."
        sys.exit(-1)

    #give default project to only numeric results
    if re.match("^\d+$", issue):
        # only numeric ... try to look up known projects
        repo = git.Repo()
        remote_urls = [remote.url for remote in repo.remotes]
        for url in remote_urls:
            if url in DEFAULT_PROJECTS:
                issue = "%s-%s" % (DEFAULT_PROJECTS[url],issue)
                break

    #strip JIRA- prefix from issue if present
    if issue[:5].upper() == "JIRA-":
        issue = issue[5:]
    #sanity check for branch name
    project, ignore = issue.split("-",1)
    if project not in KNOWN_PROJECTS:
        response = raw_input(
            "You appear to be starting a branch for an unknown project.  Continue? [n]" 
        )
        if not response.startswith(('y','Y')):
            sys.exit(-1)

    branch = "JIRA-%s" % issue

    # branch may exist in remote but not local
    if os.spawnlp(os.P_WAIT,"git","git","fetch") != 0:
        print "Failed to fetch from origin. Branch not created."
        sys.exit(-1)

    if len(sys.argv) <= 2:
        master = git_common.master_branch()
    else:
        master = sys.argv[2]
        if master not in [b.name for b in git.Repo().branches]:
            print "Branch %s does not exist. Have you checked it out?" % master
            sys.exit(-1)

    # try to switch to the new branch
    if os.spawnlp(os.P_WAIT,"git","git","checkout",branch) == 0:
        # if it exists, pull
        print "Pulling from origin/%s..." % branch
        os.execlp("git","git","pull","origin",branch)
    else:
        # if it doesn't exist, create it
        print "Branch doesn't exist, creating new from %s" % master
        if os.spawnlp(os.P_WAIT,"git","git","checkout", master) != 0:
            print "Failed to checkout %s, branch not created" % master
            sys.exit(-1)
        if os.spawnlp(os.P_WAIT,"git","git","pull","--ff-only","origin", master) == 0:
            if os.spawnlp(os.P_WAIT,"git","git","checkout","-b", branch, master) == 0:
                # setup remote tracking for the branch
                print "Configuring remote tracking branches"
                os.spawnlp(os.P_WAIT, "git","git","config","--replace-all", ("branch.%s.remote" % branch), "origin")
                os.spawnlp(os.P_WAIT, "git","git","config","--replace-all", ("branch.%s.merge" % branch), ("refs/heads/%s" % branch))
            else:
                print "Failed to create new branch"
                sys.exit(-1)
        else:
            print "Pull from origin/%s failed, branch not created" % master
            print "Do you have merges you haven't pushed yet? Check `git status`"
            print "If you want to reset your local to match the remote %s, run:" % master
            print "    git reset --hard origin/%s" % master
            sys.exit(-1)
