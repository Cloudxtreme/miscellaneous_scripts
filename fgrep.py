#!/usr/bin/env python
"""
Wrapper for `grep` search of files
"""

import sys
import os
import getopt
import itertools

usage=r"""
    fgrep.py -- Wrapper for grep to search file contents and easier multi-
                pattern search
    
    Usage: (tip: add `alias fgrep='/path/to/fgrep.py'` to your profile)
        
        fgrep [options] pattern [pattern2 pattern3 ...]
    
    Options: (`=` means requires input, defaults in [ ])
        -A=
            Adds the `-A` flag. Number of lines *after* to also print
        
        -B=
            Adds the `-B` flag. Number of lines *before* to also print
        
        -C=,--context=
            Adds the `-C` or `--context` flag to grep with the number.
        
        -E
            Replace the `-e` with `-E` for extended grep
               
        --grepflag=  
            Additional grep flags
                Specify as `--grepflag "-J --exclude=bla"` (etc)
        -H,--help    
            Print this help. Tip: pipe to less
        
        -h
            print short help
        
        -i
            Case insensitive. Note that this can be buggy with multiple patterns
            on BSD (mac) systems
        
        -n=,--name= 
            ['*'] Specify a file name for `--include` on grep 
        
        --OR
            Specify multiple patters as an OR opperator. Default is an AND
            opperator. See notes below for discussion. (--AND is default but 
            will work too)           
        
        -p=,--path=
            ['.'] Path
        
        -v,--verbose
            Print the command that will be executed
        
        -V
            ONLY print the command and do not run it.
        
        
    It will execute a command that looks as follows:
      $ grep -nHIR {add_flags} --include="{name}" -e"{pattern}" "{path}"  \
        2>/dev/null
    
    Multiple Patterns:
        The default setting for multiple pattersn is to have them behave as AND
        but you can make it behave as OR with the --OR flag.
        
        More complex behavior must be done manually (and surround with `"`)
        
        In grep, to perform the OR search, multiple `-e` flags are used. To 
        perform an AND search, all permutations of the patters are combined with
        `.*` then an OR search is performed
        
        Ex:
            | Input          | System Call              |
            |----------------|--------------------------|
            | fgrep A B      | [....] -e"A.*B" -e"B.*A" |
            | fgrep --OR A B | [....] -e"A" -e"B"       |
        
        Also note that coloring may be messed up for multiple arguments
    
    Tips: 
     * In your .bash_profile add the following:
        
        export GREP_OPTIONS='--exclude-dir=.svn --exclude-dir=.git --color=auto'    
     
       to color the output and exclude version control files
     
    Written by Justin Winokur, 2016-06    
    """
short_usage="""\
    fgrep.py -- Wrapper for grep to search file contents and easier multi-
                pattern search
    
    Usage: (tip: alias this as fgrep)
        
        fgrep [options] pattern [pattern2 pattern3 ...]
    
    See  `fgrep -H` for more detailed help (it's long so pipe to less)
    
    Written by Justin Winokur, 2016-06
"""

inputs = sys.argv[1:]

fixFlags = ['name','path']
for flag in fixFlags:
    for ii,input in enumerate(inputs):
        if input.startswith('-' + flag):
            inputs[ii] = '-' + inputs[ii]

try:
    opts, args = getopt.getopt(inputs, "A:B:C:EHhin:p:vV", ["AND","context=","grepflag=","help","name=","fname=","OR","path=","verbose"])
except getopt.GetoptError as err:
    print str(err) #print error
    print "\n Printing Help:\n"
    print usage
    sys.exit(2)   

cmdDict = {}
cmdDict['grepflags'] = ['-n','-H','-I','-R'] # Default
#     n : Print line numver
#     H : Print file name
#     I : (essentially) Ignore binary
#     R : Recursive  
cmdDict['name'] = '*'
cmdDict['path'] = '.'
verbose = False
runCMD = True
sep="-e"
ORflag = False

for o,a in opts:
    if o in ["--AND"]:
        ORflag=False # Undocumented but just to be safe
    if o in ['-A']:
        cmdDict['grepflags'] += ['-A{0:s}'.format(a)]
    if o in ['-B']:
        cmdDict['grepflags'] += ['-B{0:s}'.format(a)]
    if o in ['--context','-C']:
        cmdDict['grepflags'] += ['-C{0:s}'.format(a)]
    if o in ["-E"]:
        sep='-E'
    if o in ['--grepflag']:
        cmdDict['grepflags'] += [a]
    if o in ["-H", "--help"]:
        print usage
        sys.exit()
    if o in ['-h']:
        print short_usage
        sys.exit()
    if o in ['-i']:
        cmdDict['grepflags'] += ['-i']
    if o in ['-n','--name','--fname']:
        cmdDict['name'] = a
    if o in ["--OR"]:
        ORflag = True
    if o in ['-p','--path']:
        if a.endswith('/'):
            a = a[:-1]
        cmdDict['path'] = a
    if o in ['-v','--verbose']:
        verbose = True
    if o in ['-V']:
        verbose = True
        runCMD = False

cmdDict['grepflags'] = ' '.join(cmdDict['grepflags'])

if len(args) == 0:
    print "must specify a pattern. Printing help \n"
    print usage
    sys.exit(2)

if '-i' in cmdDict['grepflags']:
    args = [arg.lower() for arg in args] # Not really needed but makes removing duplicates easier

args = list(set(args)) # Remove duplicates

if not ORflag: # All permutations making it act like "AND"
    args = ['.*'.join(arg) for arg in list(itertools.permutations(args))]
args = [sep + '"' + arg + '"' for arg in args] # Combine in an OR fashion
 
cmdDict['pattern'] = ' '.join(args)

cmd = 'grep {grepflags:s} --include="{name:s}" {pattern:s} "{path:s}" 2>/dev/null'.format(**cmdDict)


if verbose:
    print("Executing:\n  $ {0:s}\n{1:s}\n".format(cmd,'-'*60))

if runCMD:
    os.system(cmd)









