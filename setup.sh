#!/usr/bin/env bash

for i in * 
do
  (test -e ~/.$i && test ! -L ~/.$i) && rm ~/.$i
  test -L ~/.$i || ln -s $(pwd)/$i ~/.$i
done
test -d ~/.git_tools/vendor || mkdir ~/.git_tools/vendor
test -e ~/.git_tools/vendor/bin/python || python ~/.git_tools/vendor/virtualenv.py --distribute ~/.git_tools/vendor/python
PIP_DOWNLOAD_CACHE=~/.git_tools/vendor/cache ~/.git_tools/vendor/python/bin/pip install gitpython jinja2
rm -f virtualenv.py*
rm -f distribute*
