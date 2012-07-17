#!/bin/bash

# Update remote branches
echo "Fetching..."
git fetch

if [[ $# -eq 0 ]]; then
    master=$(git ci-master)
else
    master="$1"
fi

echo "Remote branches not merged to origin/$master"

# Get a list of all remote branches not merged to master
# Excludes lines like "origin/HEAD -> origin/test"
for branch in $(git branch -r --no-merged origin/$master | grep -v '[^ ] '); do
    # Only check/color JIRA branches
    if [[ "$branch" == *JIRA-* ]]; then
	# See if there's a tag at the end of the branch
	# Use 2>/dev/null to block "fatal: no tag exactly matches"
	tag=$(git describe --tags --exact-match $branch 2>/dev/null);
	# See if the tag is a SIGNOFF tag
	if [[ "$tag" == *-SIGNOFF-* ]]; then
	    # Print out JIRA branch in green with SIGNOFF tag
	    if [ -t 1 ]; then printf "\033[32m"; fi
	    echo "  $branch ($tag)"
	else
	    # Print out JIRA branch in red
	    if [ -t 1 ]; then printf "\033[31m"; fi
	    echo "  $branch"
	fi
    else
	# Print out non-JIRA branch in default color
	if [ -t 1 ]; then printf "\033[m"; fi
	echo "  $branch"
    fi
done

# Reset to normal colors
if [ -t 1 ]; then printf "\033[m"; fi
