#!/usr/bin/env bash

## History settings

# Write/append history on all commands (universal history)
#  from http://www.ukuug.org/events/linux2003/papers/bash_tips/
shopt -s histappend
PROMPT_COMMAND='command history -a'

# Improved PROMPT_COMMAND to append information at the end. (I don't use this one)
#export PROMPT_COMMAND='hpwd=$(history 1); hpwd="${hpwd# *[0-9]*  }"; if [[ ${hpwd%% *} == "cd" ]]; then cwd=$OLDPWD; else cwd=$PWD; fi; hpwd="${hpwd% ### *} ### $cwd"; history -s "$hpwd"'

# Do not add certain commands to the history to prevent accidents
# This includes deletions and resets
export HISTIGNORE='rm *:git reset *:git checkout *:rmdir *'
# Additional ones to consider: find *xargs* rm*:find*-exec*rm*

# Do not include other commands that start with a space
export HISTCONTROL=ignorespace

export HISTFILESIZE=2500


pwd2hist() {
    ppwd=$(eval "pwd")
    hh="# pwd: $ppwd"
    command history -s "$hh"
    echo "$hh"
}

# lastcmd was here. Deleted AFTER [git: setup_config] 2ca3086686:bash_profile_source/ (2016-08-17 08:28:53 -0600)

alias history="history | cut -c 8- |sed 's/^/    $ /'"
# alias histmd="history_md"

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
