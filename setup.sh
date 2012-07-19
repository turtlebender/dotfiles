#!/usr/bin/env bash

for i in * 
do
  (test -e ~/.$i && test ! -L ~/.$i) && rm ~/.$i
  test -L ~/.$i || ln -s $(pwd)/$i ~/.$i
done
test -d ~/.git_tools/vendor || mkdir ~/.git_tools/vendor
test -e ~/.git_tools/vendor/bin/python || python ./vendor/virtualenv.py --distribute ~/.git_tools/vendor/python
PIP_DOWNLOAD_CACHE=~/.git_tools/vendor/cache ~/.git_tools/vendor/python/bin/pip install gitpython jinja2
python ./vendor/virtualenv.py --distribute $(pwd)/tools/flake8
pushd $(pwd)/tools/flake8
$(pwd)/bin/python $(pwd)/setup.py install
popd
test -d ~/tools || ln -s $(pwd)/tools ~/tools
rm -f virtualenv.py*
rm -f distribute*
test -d ~/bin || mkdir ~/bin
test -L ~/bin/flake8 || ln -s $(pwd)/tools/flake8/bin/flake8 ~/bin/flake8

pushd tools/foodcritic
bundle install --local --path vendor
popd
test -L ~/bin/foodcritic || ln -s ~/tools/foodcritic/foodcritic ~/bin/foodcritic
