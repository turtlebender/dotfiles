import sys
import git_common

if __name__ == "__main__":
    if len(sys.argv) == 1: # No args
        print git_common.master_branch()
    elif len(sys.argv) == 2: # One arg
        try:
            git_common.master_branch(sys.argv[1])
        except Exception as e:
            for arg in e.args:
                print str(arg)
            sys.exit(-1)
    else:
        print "Usage: git ci-master [ [new master] ]"
        sys.exit(-1)
