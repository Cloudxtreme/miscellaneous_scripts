#!/usr/bin/env bash

## History settings

shopt -s histappend


## Option 1:  Write/append history on all commands (universal history)

# PROMPT_COMMAND='command history -a'
    
    # Do not add certain commands to the history to prevent accidents
    # This includes deletions and resets
# export HISTIGNORE='rm *:git reset *:git checkout *:rmdir *'
    # Additional ones to consider: find *xargs* rm*:find*-exec*rm*

## Option 2: Append  comment to certain commands.

# This will filter the history to add a comment in front of certain 
# "dangerous" commands so they won't be run again but will be in the history
# note the different specification from HISTIGNORE above.
#       rm *  --> "rm "*    or    git reset * --> "git reset "*
# and `|` instead of `:`

function hist_mod(){
    cmd="$*"
#     D=`pwd`
    case "$cmd" in 
        "rm "*|"git reset "*|"git checkout "*|"rmdir "*|"find"*"xargs"*"rm"|"find"*"-exec"*"rm"*|"find"*"parallel"*"rm"|"sudo "*|"git commit -am"*|"git commit -m"*)
            cmd="#"$cmd"  # auto-commented"; ;;
    esac;
    cmd="$cmd"
    command history -s "$cmd"
}
export PROMPT_COMMAND='hpwd=$(command history 1); hpwd="${hpwd# *[0-9]*  }"; hist_mod $hpwd'


##### Other:

# Do not include other commands that start with a space
export HISTCONTROL=ignorespace
export HISTSIZE=5000


pwd2hist() {
    ppwd=$(eval "pwd")
    hh="# pwd: $ppwd"
    command history -s "$hh"
    echo "$hh"
}

# lastcmd was here. Deleted AFTER [git: setup_config] 2ca3086686:bash_profile_source/ (2016-08-17 08:28:53 -0600)

alias history="history | cut -c 8- |sed 's/^/    $ /'"

histtail() { # Display the last n (default 10) history enties excluding this one
    if [ -z "$1" ]; then
        n=10
    else
        n=$@
        n=$(echo $n|sed 's|[^0-9]||g') # Allow for "-n 10" or just "10" for example
    fi
    nt=$(($n+1))
    eval "history | tail -n $nt | head -n $n"
}
alias hist="histtail"
