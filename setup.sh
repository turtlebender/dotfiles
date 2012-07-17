#!/usr/bin/env bash

(test -e ~/.bashrc && test ! -L ~/.bashrc) && rm ~/.bashrc
test -L ~/.bashrc || ln -s $(pwd)/bashrc ~/.bashrc

(test -e ~/.vimrc && test ! -L ~/.vimrc) && rm ~/.vimrc
test -L ~/.vimrc || ln -s $(pwd)/vimrc ~/.vimrc

(test -e ~/.vim && test ! -L ~/.vim) && rm -r ~/.vim
test -L ~/.vim || ln -s $(pwd)/vim ~/.vim

(test -e ~/.git_tools && test ! -L ~/.git_tools) && rm -r ~/.git_tools
test -L ~/.git_tools || ln -s $(pwd)/git_tools ~/.git_tools
test -d ~/.git_tools/vendor || mkdir ~/.git_tools/vendor
test -L ~/.git_tools/vendor/virtualenv.py || ln -s $(pwd)/virtualenv.py ~/.git_tools/vendor/virtualenv.py
test -e ~/.git_tools/vendor/bin/python || python ~/.git_tools/vendor/virtualenv.py --distribute ~/.git_tools/vendor/python
PIP_DOWNLOAD_CACHE=~/.git_tools/vendor/cache ~/.git_tools/vendor/python/bin/pip install gitpython jinja2

(test -e ~/.gitconfig && test ! -L ~/.gitconfig) && rm ~/.gitconfig
test -L ~/.gitconfig || ln -s $(pwd)/gitconfig ~/.gitconfig
