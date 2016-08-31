#!/usr/bin/env python

import os
import sys
import subprocess
import getopt

def usage():
    usage ="""
    gitpath.py
        
        Get the relative git path in the following format
        
            `[git: repoName] hash:path`
        
        where `hash` is the first 10 (or user-set) digits of the last hash
        for the file itself and NOT necessarily the entire repo and the `path`
        is relative to the repo base.
        
        or fuller details
        
    Usage: (add `alias gitpath='/path/to/gitpath.py'` to your profile)
        gitpath [OPTIONS] path1 (path2 path3 ...)
    
    Options:
        -a,--all        : Display all digits of the hash
        -b,--branch     : Display the branch
        -d,--date       : Do **NOT** display the date of the commit
        -f,--full       : Prints all information and overrides as needed
        -h,--help       : Display help
        -L,--Last       : Display the hash of the last commit of the entire
                          repo, rather than the file itself.
        -m,--md         : Prints in a markdown format
        -N=,--hashN=    : [10] How many digits of the hash to display
    
    (if `-N=` and `-a` are specified, whichever comes last will prevail)
    
    The final result should be enough to recover a specific file. Even if
    the hash changes (from a rebase for example) the exact date should help
    
    """
    print usage

hashN = 10
 
def GitPath(path,hashN=10,last=False,datePrint=False,silent=False,branch=False,full=False,md=False):

    # Get the absolute path
    path = os.path.abspath(path)

    isDir = os.path.isdir(path)

    if isDir:
        DirPath = path
        FileName = ''
    else:
        FileName = os.path.basename(path)
        DirPath = os.path.dirname(path)

    # Make sure it ends with a '/'
    if not DirPath.endswith('/'):
        DirPath += '/'

    # get the initial path then move to the new one
    DirPath0 = os.getcwd()
    os.chdir(DirPath)
    
    ### File Paths
    
    try:
        GitRoot = subprocess.check_output('git rev-parse --show-toplevel'.split())
    except subprocess.CalledProcessError:
        print('Specified path is not in a git repo')
        return
     
    GitRoot = GitRoot.strip()

    # Make sure it ends in a '/'
    if not GitRoot.endswith('/'):
        GitRoot += '/'

    # Try to get the git Name
    RepoName = os.path.basename(GitRoot[:-1])

    # Git Branch
    branchName = [b for b in subprocess.check_output(['git','branch']).split('\n') if b.startswith('*')][0][2:]
    
        
    # Relative Path
    if isDir:
        RelPath = os.path.relpath(DirPath,GitRoot)
        if not RelPath.endswith('/'):
            RelPath += '/'
    else:
        cmd = 'git ls-tree --full-name --name-only HEAD -- {:s}'.format(FileName)
        RelPath = subprocess.check_output(cmd.split(),stderr=subprocess.STDOUT).strip()

#     Make sure it ends in a '/'
#     if not RelPath.endswith('/'):
#         RelPath += '/'
# 
#     Combine to print:
#     if not isDir:
#         RelPath += FileName

    if RelPath.startswith('./'):
        RelPath = RelPath[2:] 

    ### Info

    repoHash = subprocess.check_output('git rev-parse HEAD'.split())
    repoHash = repoHash.strip()
    repodate = subprocess.check_output('git log -1 --format=%cd --date=iso'.split()).strip()
    
    Hash,date = parse_log_filepath(FileName) 
           
    
    if not hashN =='all' and not full:
        Hash = Hash[:hashN]
        repoHash = repoHash[:hashN]
    
    if not full:
        if branch:
            RepoName = RepoName + ":" + branchName

        if not last:
            Hash = repoHash
            date = repodate
        
        text = '[git: {0:s}] {1:s}:{2:s}'.format(RepoName,Hash,RelPath)
    
        if datePrint:
            text += ' (' + date + ')'
        
        text = '* `' + text + '`'
    else:
        text  = '* git repo: `{0:s}`\n'.format(GitRoot)
        if isDir:
            text += '    * Folder: `{0:s}` \n'.format(RelPath)
        else:
            text += '    * File: `{0:s}` \n'.format(RelPath)
        text += '    * HEAD: `{0:s} ({1:s})`\n'.format(repoHash,repodate)
        text += '    * Branch: `{0:s}` \n'.format(branchName)
        text += '    * Hash: `{0:s} ({1:s})`'.format(Hash,date)
        
    
    if not md:
        text = text.replace('`','').replace('* ','')
      
    # Change back paths (for if entering more than one path)
    os.chdir(DirPath0)
    
    if not silent:
        print(text)
    
    return text

def parse_log_filepath(FileName):
    """
    Return the commit info of the current `FileName` (we're already in the
    correct directory) as opposed to the info of the whole repo
    """
    if len(FileName) == 0:
        FileName = '.'
    
    cmd = 'git log -1 --date=iso -- {0:s}'.format(FileName)
    gitlog = subprocess.check_output(cmd.split())
    
    if len(gitlog) == 0:
        print("Specified path is under git...or another issue")
        sys.exit(2)
    
    gitlog = gitlog.split('\n') # make it a list by line
    
    Hash = gitlog[0]
    Hash = Hash.replace('commit','').strip()
    
    for line in gitlog:
        if not line.startswith('Date:'):
            continue
        date = line.split(':',1)[-1].strip()
        break
    return Hash,date

    

    
if __name__=='__main__':
    # I prefer getopt to argparse. To each his/her own....
    try:
        opts, args = getopt.getopt(sys.argv[1:], "abdfhLmN:", ["all","branch","date","full","help","Last","md","hashN="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print "\n Printing Help:\n"
        usage()
        sys.exit(2)
    
    hashN = 10
    last = True
    datePrint = True
    branch = False
    full = False
    md = False
    
    for  o,a in opts:
        if o in ("-a", "--all"):
            hashN = 'all'
        if o in ("-b","--branch"):
            branch = True
        if o in ("-d","--date"):
            datePrint = False
        if o in ("-f","--full"):
            full=True
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ('-L','--Last'):
            last = False
        if o in ('-m','--md'):
            md = True
        if o in ("-N","-hashN"):
            hashN = int(a)
    if len(args)==0:
        args = ['.']

    for path in args:
        GitPath(path,hashN=hashN,last=last,datePrint=datePrint,branch=branch,full=full,md=md)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
