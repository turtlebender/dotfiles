#!/usr/bin/env bash

(test -e ~/.bashrc && test ! -L ~/.bashrc) && rm ~/.bashrc
test -L ~/.bashrc || ln -s $(pwd)/bashrc ~/.bashrc

(test -e ~/.vimrc && test ! -L ~/.vimrc) && rm ~/.vimrc
test -L ~/.vimrc || ln -s $(pwd)/vimrc ~/.vimrc

(test -e ~/.vim && test ! -L ~/.vim) && rm -r ~/.vim
test -L ~/.vim || ln -s $(pwd)/vim ~/.vim

(test -e ~/.gitconfig && test ! -L ~/.gitconfig) && rm ~/.gitconfig
test -L ~/.gitconfig || ln -s $(pwd)/gitconfig ~/.gitconfig
