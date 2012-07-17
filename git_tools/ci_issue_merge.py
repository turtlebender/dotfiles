
import os
import sys
import git
import re

import git_common

if __name__ == "__main__":
    try:
        tag = sys.argv[1]
    except:
        print "You must include a signed tag."
        sys.exit(-1)

    if not re.match("^JIRA-.*-SIGNOFF-\d+$", tag):
        response = raw_input(
            "This doesn't appear to be a signoff tag.  Continue? [n]" 
        )
        if not response.startswith(('y','Y')):
            sys.exit(-1)

    #Fetch first
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

    #TODO: Add a large divergence sanity check statement here
    #This would imply a merge to the wrong branch

    # Find the (all) tags with this tag name
    tags = filter(lambda t: t.name == tag, git.Repo().tags)
    if len(tags) < 1:
        print "Could not find tag %s" % tag
        sys.exit(-1)
    elif len(tags) > 1:
        print "Found more than one tag %s. How did you do this?" % tag
        sys.exit(-1)

    # Get the message and extract MERGE: lines
    message = tags[0].tag.message
    mlines = filter(lambda l: l[:7].upper() == "MERGE: ",message.split('\n'))

    if len(mlines) < 1:
        response = raw_input("Could not find a MERGE: line.  Continue? [n]")
        if not response.startswith(('y','Y')):
            sys.exit(-1)

    # If there are no merge lines, allow merge
    allow = True
    for l in mlines:
        if " > " not in l: continue
        if l.split(" > ")[1] == master:
            # If there is a merge line for master, allow merge
            allow = True
            break
        else:
            # If there is a merge line for not master, get suspicious
            allow = False

    if not allow:
        response = raw_input("Could not find a \"MERGE: %s > %s\" line.  Continue? [n]" % (tag,master))
        if not response.startswith(('y','Y')):
            sys.exit(-1)

    #Attempt merge
    try:
        git_cmd = git.Git()
        
        print "Verifying tag..."
        print git_cmd.tag("-v",tag)

        print "Switching to %s..." % master
        print git_cmd.checkout(master)

    except git.GitCommandError as e:
        print "Failed due to %s" % str(e)
        sys.exit(-1)
      
    print "Pulling from origin/%s..." % master
    if os.spawnlp(os.P_WAIT,"git","git","pull","--ff","origin", master) == 0:
        print "Merging %s into %s" % (tag, master)
        if os.spawnlp(os.P_WAIT,"git","git","merge","--no-ff", tag) == 0:
            print "Merge successful. Use `git push origin %s` to push to remote" % master
        else:
            print "Merge failed. If there are merge conflicts, please resolve them, commit, and push"
            sys.exit(-1)
    else:
        print "Pull failed, unable to merge to %s" % master
        print "If you want to reset your local to match the remote %s, run:" % master
        print "    git reset --hard origin/%s" % master
        sys.exit(-1)
