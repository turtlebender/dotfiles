#!/usr/bin/env python

import os
import os.path
import sys
import logging
import git
import re
from jinja2 import Template
from StringIO import StringIO
from git_common import ALLOWED_HOOKS, get_relative_file


def main(argv):
    try:
        repo = git.Repo()
        hook_name = os.path.basename(argv[0])
        handler_name = hook_name.replace('-','_')
        #if allowed and a handler exists, call it
        if hook_name in ALLOWED_HOOKS and handler_name in globals():
            handler = globals()[handler_name]
            return handler(repo, *argv[1:])
        else:
            #otherwise exit quietly
            return 0
    except Exception as e:
        logging.exception(e)
        sys.exit(-1)

def post_checkout(repo, old_ref, new_ref, branch_checkout):
    reader = repo.config_reader()
    chef_repo = 'globusonline/chef-repo'
    try:
        chef_version = reader.get('chef-repo','personal-version')
    except:
        chef_version = '9.9.9'
    if chef_repo in reader.get('remote "origin"', 'url') and branch_checkout == "1":
        if repo.active_branch.name == 'integration':
            chef_version = '1.0.0'
        if repo.active_branch.name == 'production':
            chef_version = '3.0.0'
        if repo.active_branch.name.startswith('RELEASE'):
            chef_version = '2.0.0'
        for file in os.listdir(os.path.join(repo.working_dir, 'cookbooks')):
            with open(os.path.join(repo.working_dir, 'cookbooks', file, '.version'), 'w') as version_file:
                version_file.write(chef_version)


def prepare_commit_msg(repo, commit_file, *args):

    params = {}
    template_file = get_relative_file("jinja_templates", "commit_template.txt")

    with open(template_file) as f:
        template = Template(f.read())
        source_config = StringIO(template.render(params))

    # save the configured template
    with open(commit_file, 'r+') as f:
        # TODO: Handle template, merge, squash, and commit as well?
        if len(args) > 0 and args[0] == "message": # commit -m
            # Just use the message provided
            # Otherwise the commented lines
            # show up in the commit message
            pass
        else: # commit (editor)
            orig_content = StringIO(f.read())
            f.seek(0)
            f.write("\n") #Leave a blank line for the commit message
            f.write(source_config.getvalue())
            f.write(orig_content.getvalue())
    

def commit_msg(repo, msg_file):
    branch = repo.active_branch.name

    if not branch: 
        logging.error("Could not determine branch name")
        return -1

    with open(msg_file, "r") as f:
        msg = f.read()


    # Fixes are all bugs labeled with "FIXES: <bug_name>"
    pivotal_fixes = set(extract_tickets("PIVOTAL", *extract_tag_line("FIXES", msg)))
    jira_fixes = set(extract_tickets("JIRA", *extract_tag_line("FIXES", msg)))

    # Relateds are all bugs labeled with "RELATED:" or named branch, or named in
    # a bug branch, but not listed as a fix
    jira_related = set(
        extract_tickets("JIRA", *extract_tag_line("RELATED", msg)) + 
        extract_tickets("JIRA", branch)
    ) - pivotal_fixes
    pivotal_related = set(
        extract_tickets("PIVOTAL", *extract_tag_line("RELATED", msg)) + 
        extract_tickets("PIVOTAL", branch)
    ) - pivotal_fixes


    # write out additional tag lines
    with open(msg_file, "a") as f:
        # TODO: Figure out the correct transition number
        for ticket in jira_related:
            trigger = "[#%s transition:31]\n" % ticket
            f.write(trigger)

        for ticket in pivotal_related:
            trigger = "[Story%s]\n" % ticket
            f.write(trigger)

        # TODO: Figure out the correct transition number
        for ticket in jira_fixes:
            trigger = "[#%s transition:31]\n" % ticket
            f.write(trigger)

        for ticket in pivotal_fixes:
            trigger = "[Story%s status:complete]\n" % ticket
            f.write(trigger)

    return 0


def extract_tickets(prefix, *strings):
    """
    Extracts ticket numbers from list of strings.  Looks for a prefix and 
    extracts the corresponding ticket number.
    """
    tickets = [
        ticket 
        for string in strings 
        for ticket in re.findall("\\b%s-([-_a-zA-Z0-9]*)\\b" % prefix, string)
    ]
    return tickets

def extract_tag_line(prefix, *strings):
    """
    Returns a list of lines that begin with a given tag.
    """
    tag_lines = [
        tag_line 
        for string in strings 
        for tag_line in re.findall("^%s: .*$" % prefix, string, flags=re.M)
    ]
    return tag_lines


if __name__ == "__main__":
    sys.exit(main(sys.argv))
