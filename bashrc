# Chef assumes that it owns this file.
# Additions to bash should be placed into $HOME/.bash_profile_includes/ with a .sh extension

if [ -e ${HOME}/.bash_profile_includes ] ; then
  for file in $(\ls -1 ${HOME}/.bash_profile_includes/*.sh); do
    source $file;
  done
fi

function parse_git_branch {
  ref=$(git-symbolic-ref HEAD 2> /dev/null) || return
  echo "("${ref#refs/heads/}")"
}

RED="\[\033[0;31m\]"
YELLOW="\[\033[0;33m\]"
GREEN="\[\033[0;32m\]"

PS1="$RED\$(date +%H:%M) \w$YELLOW \$(parse_git_branch)$GREEN\$ "
if [ -e ~/bash_completion ] ; then
  for i in ~/bash_completion/* ; do source $i ; done
fi

PATH="./bin":$PATH
export EDITOR=vi

export LSCOLORS='Gxfxcxdxdxegedabagacad'
alias l='ls -GFp' 
alias ll='ls -lFh'
alias la='ls -AFlh'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias ping='ping -c 5'
alias df='df -h'
alias du='du -h -c'
alias clr='clear;echo "Currently logged in on $(tty), as $(whoami) in directory $(pwd)."'
alias pycclean='find . -name "*.pyc" -exec rm {} \;'
alias pypath='python -c "import sys; print sys.path" | tr "," "\n" | grep -v "egg"'

extract () {
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)        tar xjf $1        ;;
            *.tar.gz)         tar xzf $1        ;;
            *.bz2)            bunzip2 $1        ;;
            *.rar)            unrar x $1        ;;
            *.gz)             gunzip $1         ;;
            *.tar)            tar xf $1         ;;
            *.tbz2)           tar xjf $1        ;;
            *.tgz)            tar xzf $1        ;;
            *.zip)            unzip $1          ;;
            *.Z)              uncompress $1     ;;
            *)                echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

dict() {
    grep "$@" /usr/share/dict/words
}

dgrep() {
    # A recursive, case-insensitive grep that excludes binary files
    grep -iR "$@" * | grep -v "Binary"
}
dfgrep() {
    # A recursive, case-insensitive grep that excludes binary files
    # and returns only unique filenames
    grep -iR "$@" * | grep -v "Binary" | sed 's/:/ /g' | awk '{ print $1 }' | sort | uniq
}
psgrep() {
    if [ ! -z $1 ] ; then
        echo "Grepping for processes matching $1..."
        ps aux | grep $1 | grep -v grep
    else
        echo "!! Need name to grep for"
    fi
}

tree () {
    find $@ -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
}

mcd () {
    mkdir "$@" && cd "$@"
}

exip () {
    # gather external ip address
    echo -n "Current External IP: "
    curl -s -m 5 http://myip.dk | grep "<title>" | sed -e 's/<title>Your IP address is: //g' -e 's/<\/title>//g'
}

ips () {
    # determine local IP address
    ifconfig | grep "inet " | awk '{ print $2 }'
}
export PYTHONPATH=~/src/globusonline/ci-dev-tools/git_tools
export PROJECT_HOME=$HOME/src
export LESS=-RFX
alias less="less -RFX"

alias vi=vim
export PATH=/usr/local/bin:/usr/local/Cellar/ruby/1.9.3-p0/bin:$PATH

function kill_vim() {
  pid=`ps aux|grep vim|grep -v grep |grep $1 | tr -s ' ' |cut -d ' ' -f 2`
  kill -9 $pid
}

_fab_completion() {
	    COMPREPLY=( $( \
				    COMP_LINE=$COMP_LINE  COMP_POINT=$COMP_POINT \
						    COMP_WORDS="${COMP_WORDS[*]}"  COMP_CWORD=$COMP_CWORD \
								    OPTPARSE_AUTO_COMPLETE=1 $1 ) )
}

complete -o default -F _fab_completion fab
export PATH=/usr/local/share/python:$PATH

[[ -s $HOME/.pythonbrew/etc/bashrc ]] && source $HOME/.pythonbrew/etc/bashrc
export PATH=~/bin:$PATH
alias b="bundle"
alias bi="b install --path vendor"
alias bil="bi --local"
alias bu="b update"
alias be="b exec"
alias binit="bi && b package && echo 'vendor/ruby' >> .gitignore"
alias foreman="be foreman"
