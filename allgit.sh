#!/usr/bin/env bash

show_help(){
echo " #####################################################
 allgit.sh (or aliased as 'agit')                     
    Perform the git command on all direct subfolders  
    if it is a git repo (ie, has a .git directory)    
    or deeper with the -d flag. See options for more. 
                                                      
 Usage:  [aliased as agit]                                             
     agit [options] command                    
                                                      
        Executes 'git command' on all repos           
 Options (an = requires input):                       
     -c  :   execute whole command without 'git' on   
             all git repos.                           
             Example: The following are identical     
                  agit -c git status           
                  agit status                  
     -d= :   [1] How many sub-directories below to    
             search for git repos                     
     -h  :   display help                             
     -p  :   Pause after each. Will also clear screen 
                                                      
 Tip: Add the following to your bash_profile          
          alias agit=/path/to/allgit.sh               
 
 Note: only works on non-bare repos
                                                      
 Written By: Justin Winokur, 2016
                                   
 #####################################################"
}

######################### Parse Input
## Adapted from http://stackoverflow.com/a/14203146
# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
cmd=0
pause=0
depth=2

while getopts "cd:h?p" opt; do
    case "$opt" in
    c)  cmd=1
        ;;
    d)  depth=`echo $OPTARG+1 |bc`
        ;;
    h|\?)
        show_help
        exit 0
        ;;
    p)  pause=1
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

##########################################

# Use find to get all git-repo sub folders (depth + 1). Use sed to clean up output
REPOS=`find -L . -maxdepth $depth -type d -name ".git" 2> /dev/null |sed 's%\./%%g' | sed 's%/\.git%%g' |sort `

pwd0=$(pwd)

for repo in $REPOS; do
    if [ $pause == 1 ]; then
        clear
    fi
    
    if [ $repo == ".git" ]; then
        echo "-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ "
        echo " Note:                                       "
        echo " Inside a git repo. Running on parent folder "
        echo "=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ "
        repo='.'
    fi
    
    echo "$repo:"
    echo "======"
    cd $repo 
        
        if [ $cmd == 0 ]; then
            eval "git $@"
        else
            eval "$@"
        fi
        
        echo '--------------------------------------------------'
        if [ $pause == 1 ]; then
            read -p "Press any key to continue (or CTRL-C to break)"
            echo '=================================================='
        fi
    cd $pwd0

done
