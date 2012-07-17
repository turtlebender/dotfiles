#!/usr/bin/env python

import sys
import logging
import os
from textwrap import dedent
from jinja2 import Template
from StringIO import StringIO
from git_common import get_relative_file
from getpass import getpass

try:
    import git
except:
    print(dedent("""
    You don't have python-git currently installed.  To use the
    installed git hooks, you will need to execute the following:
        pip install GitPython
    """))
    sys.exit(-1)

from git_common import ALLOWED_HOOKS

def main(argv):
    try:
        # we need to install symlinks 
        print("Installing hook symlinks ...")
        create_git_template_symlinks()

        # now, you need to use our template directory
        print("Configuring templates ...")
        git_config()

        print(dedent("""
              Git is ready for you to start using. If you have already checked
              out a repository run `git init` in the repository directory to
              reconfigure git.
              """))
        return 0 
    except Exception as e:
        logging.exception(e)
        return -1

def git_config_template_dir():
    """
    Sets the global git template directory to the CI default template.
    """

    g = git.Git()

    logging.info("Setting default config directory globally.")
    g.config('--global', 'init.templatedir', template_dir) 

def git_config():
    """
    Sets name and email address in global config.  We don't want any anonymous
    commits.  Also copies standard git config aliases to global config.
    """
    print "configure git"
    g = git.Git()

    params = dict()

    #gather template params
    try:
        params['name'] = g.config('--global', 'user.name')
    except git.GitCommandError:
        params['name'] = raw_input("Enter your name: ")

    try:
        params['email'] = g.config('--global', 'user.email')
    except git.GitCommandError:
        params['email'] = raw_input("Enter your email address: ")

    try:
        params['jira_server'] = g.config('--global', 'jira.server')
    except git.GitCommandError:
        params['jira_server'] = raw_input("Please enter your JIRA server: ")

    try:
        params['jira_user_name'] = g.config('--global', 'jira.username')
    except git.GitCommandError:
        params['jira_user_name'] = raw_input("Please enter your JIRA user name: ")

    try:
        params['jira_password'] = g.config('--global', 'jira.password')
    except git.GitCommandError:
        params['jira_password'] = getpass("Please enter your JIRA password " +
            "(will be stored in plaintext, leave blank for a runtime prompt): ")

    params['template_dir'] = "templates"
    params['pwd'] = os.path.dirname(os.path.realpath(__file__))
    template_file = get_relative_file("jinja_templates", "global.conf")
    
    with open(template_file) as f:
        template = Template(f.read())
        source_config = StringIO(template.render(params))

    #hack to make git config parser happy ... it expects a name for the file
    source_config.name = "tmp"
    git_merge_global_config(source_config)

def git_merge_global_config(source_config):
    """Adds all of source_configs values to the global config"""
    source_parser = git.GitConfigParser(source_config)
    global_config = os.path.expanduser('~/.gitconfig')
    global_parser = git.GitConfigParser(global_config, False)

    for section in source_parser.sections():
        for option, value in source_parser.items(section):
            print "Config: %s.%s = %s" %( section, option, value)

            if not global_parser.has_section(section):
                global_parser.add_section(section)
            global_parser.set(section, option, value)

    #Write out changes
    global_parser.write()
            
def create_git_template_symlinks():
    """
    Constructs absolute path symlinks in the template directory to the CI
    git hook handler.
    """

    hook = get_relative_file("git_hook.py")
    hook_dir = get_relative_file("templates", "hooks")
    

    for action in ALLOWED_HOOKS:
        hook_link = os.path.join(hook_dir, action)
        try:
            os.symlink(hook, hook_link)
        except OSError as e:
            if e.errno == os.errno.EEXIST:
                os.unlink(hook_link)
                os.symlink(hook, hook_link)
            else:
                raise

if __name__ == "__main__":
    sys.exit(main(sys.argv))
