
import os
import sys

if __name__ == "__main__":
    try:
        release = sys.argv[1]
    except:
        print "You must include a release id."
        sys.exit(-1)

    branch = "RELEASE-%s" % release
    # try to switch to the new branch
    if os.spawnlp(os.P_WAIT,"git","git","checkout",branch) != 0:
        # if it doesn't exist, create it
        print "Branch doesn't exist, creating new from integration"
        os.execlp("git","git","checkout","-b", branch, "integration")
