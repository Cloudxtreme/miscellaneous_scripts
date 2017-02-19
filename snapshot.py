#!/usr/bin/env python

import getopt
import os
import sys
import shutil
import subprocess
from datetime import datetime,timedelta

usage = """
snapshot.py -- Perform rsync-based backups and prune them

Usage:
    
    ./snapshot.py [FLAGS] source [dest]
    
Arguments:

    source
        Source folder
    
    dest (optional)
        destination folder. If not specified, will use a folder called 
        .snapshots in the source and add .snapshots to the excludes.
    
Options:
    
    --exclude
        Add excludes to rsync (see also using .snapshot_excludes at source
        or dest)
    
    -h,--help
        Display this help
    
    --prune    
        Prune older snapshots after running
            * All from the last 24 hours
            * 1 per day for the past 30 days (may be extra if w/in last 24)
            * 1 per week otherwise
    
    --prune-only
        Prune older snapshots without first running. See `--prune` for details

Excludes

    Excludes are directly sent to rsync so use the appropriate rsync style.
    They may be specified at the command-line with `--exclude` and/or they may
    be specified with a .snapshot_excludes file in either the source and/or
    the dest (it will search and use both). Recall if the dest is not specified
    it will default to `source/.snapshots` 

Tips / Notes:

    * Some OSes do not correctly report the size used due to the hard-
      links. To see the size, navigate to the backup destination and
      run `du -sch *` to see the actual sizes 

Based on:

  http://blog.interlinked.org/tutorials/rsync_time_machine.html
  http://blog.interlinked.org/tutorials/rsync_addendum.yaml.html
  
ToDo:

* Make it work over SSH
"""


# Future To Do 
# * Recognize and sync over SSH (maybe)
#     * Prunning will not work very well!
# * Cron help

nowObj = datetime.now()
nowSTR = nowObj.strftime('%Y-%m-%d_%H%M%S')

class logger(object):
    def __init__(self,path):
        self.path = path
        
        folder = os.path.split(path)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self.F = open(path,'w')
        self.F.flush()
    def log(self,txt,echo=True):
        self.F.write(txt+'\n')
        self.F.flush()
        if echo:
            print txt
    def close(self):
        self.F.close()

def run_cmd(cmd):
    global log
    log.log('Running command:\n    $ {:s}\n------'.format(cmd))
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1,shell=True)

    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            if line.strip().startswith('._'): 
                continue # Some strange thing with -E on macOS
            log.log('|  ' + line.rstrip())

    proc.wait()
    
    log.log('------')
    

def start(backup_dest):
    global log
    if not os.path.exists(backup_dest):
        os.makedirs(backup_dest)
    
    log_name = os.path.join(backup_dest,'logs/' + nowObj.strftime('%Y-%m-%d_%H%M%S') + '.log')
    log = logger(log_name)
    log.log('#'*30 + '\nsnapshot.py\nTime:{:s}\n'.format(nowObj.strftime('%Y-%m-%d_%H%M%S')))

def backup(source,backup_dest):
    global log
    log.log('Backup Mode')
    
    # Make them abs path
    source = os.path.abspath(source.strip())
    backup_dest = os.path.abspath(backup_dest.strip())
    
    # Make sure the source path ends in a `/`
    if not source.endswith('/'):
        source = source + '/'

    # Make sure the dest path does NOT ends in a `/`
    if backup_dest.endswith('/'):
        backup_dest = backup_dest[:-1]

    oldSnaps = os.listdir(backup_dest)
    oldSnaps = [o for o in oldSnaps if o.startswith('20')]
    oldSnaps.sort()
    
    
    # Build the command
    cmd = 'rsync -avhh --stats ' 
    
    if sys.platform == 'darwin': # Mac extended attributes
        cmd += '-E '
    
    # Add excludes
    exclude_txt = ''
    for exclude in excludes:
        exclude_txt += ' --exclude={:s} '.format(exclude)
    
    cmd += exclude_txt
    
    src_exclude = os.path.join(source,'.snapshot_excludes')
    if os.path.exists(src_exclude):
        cmd += ' --exclude-from {:s} '.format(src_exclude)
    
    dest_exclude = os.path.join(backup_dest,'.snapshot_excludes')
    if os.path.exists(dest_exclude):
        cmd += ' --exclude-from {:s} '.format(dest_exclude)
    
    
    if len(oldSnaps) == 0:
        log.log('Initial Backup')
        log.log('   Note: The first will do a full copy. Future snapshots')
        log.log('         will use less space')
    else:
        latest = os.path.join(backup_dest,oldSnaps[-1])
        log.log('\nRunning rsync. Linked to:\n    {:s}\n'.format(latest))
        cmd += ' --link-dest={:s} '.format(latest)
    
    dest = os.path.join(backup_dest,nowSTR)
    cmd += ' {source} {dest} '.format(source=source,dest=dest)
    
    run_cmd(cmd)
    
    
def get_cut(dates):
    """
    Determine which to cut based on the schedule
    This will keep:
    
    * All from the last 24 hours
    * 1 per day for the past 30 days
    * 1 per week otherwise
    
    This algorithm uses sets to make it easy to cut. But it also wants sorted
    items for repeatability so there is some inefficiency in conversion
    """

    dates = set(dates) # This is the list of ones we have not yet looked at

    now = datetime.now()
    keep = set()
    cut = set()

    # Keep all from the last 24 hours
    now_24h = now - timedelta(1)

    for date in dates: # This one doesn't have to sort
        if date >= now_24h:
            keep.add(date)

    # Remove kept ones from the list (none get cut here)
    dates.difference_update(keep)
    
    # Keep 1 per day for the last 30 days
    last30 = set()
    now_30d = now - timedelta(30)

    for date in sorted(dates,reverse=True): # Reverse sort so newest gets kept
        if date >= now_30d:
            day_of_year = date.strftime('%j')
            if day_of_year in last30:
                cut.add(date)
            else:
                last30.add(day_of_year)
                keep.add(date)
    
    # Remove the kept ones and remoce the cut ones since we won't consider them 
    # again
    dates.difference_update(keep)
    dates.difference_update(cut)

    # Keep 1 per week for the rest
    rest = set()
    for date in sorted(dates,reverse=True): # Reverse sort so newest gets kept
        if date >= now_30d:
            year_week = date.strftime('%Y%W')
            if year_week not in rest:
                keep.add(date)
                rest.add(year_week)
            else:
                cut.add(date)
    
    return sorted(cut)
    
def run_prune(backup_dest):
    log.log('Prune Mode:')
        
    # If older than 30 days : Keep 1 per week
    # If in the last 30, keep 1 per day
    # If in the last 2 days, keep all
    oldSnaps = [o for o in os.listdir(backup_dest) if o.startswith('20')]
    dates = [datetime.strptime(d,'%Y-%m-%d_%H%M%S') for d in oldSnaps]


    cuts = [d.strftime('%Y-%m-%d_%H%M%S') for d in get_cut(dates)]

    if len(cuts) > 0: 
        log.log(' Pruned:')
    else:
        log.log(' Nothing to prune')
    
    for cut in cuts:
        fullDir = os.path.join(dest,cut)
        shutil.rmtree(fullDir)
        log.log('   {:s}'.format(cut))

    log.log(' ')
    
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ['exclude=','help','prune','prune-only'])
    except getopt.GetoptError as err:
        print str(err) #print error
        print "\n Printing Help:\n"
        print usage
        sys.exit(2)   

    prune = False
    snap = True
    excludes = []
    
    for opt,arg in opts:
        if opt in ['--exclude']:
            excludes += [arg]
        if opt in ['-h','--help']:
            print(usage)
            sys.exit()
        if opt in ['--prune']:
            prune = True
        if opt == '--prune-only':
            prune = True
            snap = False
       
    if len(args) == 1:
        source = args[0]
        dest = os.path.join(source,'.snapshots')
        excludes.append('.snapshots')
    elif len(args) == 2:
        source = args[0]
        dest = args[1]
    else:
        raise ValueError('Must specify one or two arguments')

    start(dest)
    
    excludes = list(set(excludes)) # no dups
    
    if snap:
        backup(source,dest)
    if prune:
        run_prune(dest)
    
    log.log('\nLog saved in {:s}'.format(log.path))
    log.close()














