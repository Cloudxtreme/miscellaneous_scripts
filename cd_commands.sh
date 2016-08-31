#!/usr/bin/env bash
# Overwrite `cd` for using pushd and popd
# Intended to be sourced

# Use pushd for all cd commands. Use "cd -" (or "cd -N" or "cd - N") with
# to tilde-expand (instead of popd)
# Also sets the tab name if it hasn't been set before
cccd() {
    firstchar="$(echo $1 | head -c 1)"
    if [ -z "$1" ]; then
        dir="$HOME" # Nothing specified. Go home
    elif [ "$firstchar" == "-" ]; then
        # Starts with "-". Means go back. Was it:
        #   (a) "-"
        #   (b) "-N"
        #   (c) "- N"
        next="$(echo $1 | cut -c 2- )"
        if [ -z "$next" ]; then # No number in the first variable
            if [ -z "$2" ]; then
                num=1 # case (a)
            else
                num=$2 # case (c)
            fi
        else # Number specified like "-2"
            num=$next # case (b)
        fi
#         for i in $(seq 1 ${num}); do # use popd. Removes stack
#             builtin popd >/dev/null
#             if [ $? -ne 0 ]
#             then
#                 break
#             fi
#         done
        eval "cd ~$num >/dev/null" # Go back with tilde expansion. adds to the stack
        return
    else
        dir="$@"
    fi

    if [ -f "$dir" ]; then
        echo "  >> cd to parent folder <<" ;
        folder=`dirname "$dir"`
        builtin pushd "$folder" >/dev/null
    else
        builtin pushd "$dir" >/dev/null
    fi ;

    # Set the tab name
    name=${PWD##*/}
    echo -ne "\033]0;$name\007"

}
alias cd="cccd"
alias cdo="command cd"

alias dirs="dirs -v | sort -r" # Sort to be on the bottom

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'
alias .......='cd ../../../../../..'
up(){ # move up all at once
    if [ -z "$1" ]; then
        DEEP=1
    else
        DEEP=$1
    fi
    upcmd="cd "
    for i in $(seq 1 ${DEEP}); do
        upcmd="$upcmd../"
    done

    eval $upcmd
}
