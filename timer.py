#!/usr/bin/env python
""" Command line Timer. See `usage`"""
import sys
import os,subprocess
import time
from datetime import datetime,timedelta

fmt = '%Y-%m-%d %H:%M:%S'

def usage():
    txt = """
    Terminal Python Timer - Launch timers in the background
    
    A simple timer utility that will let you set persistant timers in the 
    background and manage them.
    
    Usage: (with `alias timer=python /path/to/timer.py`)
        
        timer       # Empty argument defaults to list
        timer <minutes>
        timer <minutes> <message>
        timer help
        timer list
        timer delete <number to remove> (will list and prompt w/o number)
    
    Currently only works on Macs but is simple to extend. Must have 
    "Terminal Notifier". Install with:
    
        $ sudo gem install terminal-notifier 
    
    """
    return txt


def _manage(prompt,rm=None):
    text = '\nTimers: (sorted by end time)\n'
    try:
        files = os.listdir('/var/tmp/timer/')
    except OSError:
        print "No running timers"
        sys.exit()
    
    files = [f for f in files if not f.startswith('.')]
    files.sort()
        
    ii = 0;
    iname = {}
    for file in files:
        try:
            ftime = float(file)
        except:
            continue # Not a numer
        
        # Use this time to clear old ones that may have stuck around (or failed?)
        if ftime < (time.time()+1):
            os.remove('/var/tmp/timer/' + file)
            continue
        
        with open('/var/tmp/timer/' + file,'r') as F:
            ii +=1
            text += '    {:2d}: {:s}\n'.format(ii,F.read().strip())
            iname[ii] = file
            
    if ii == 0:
        print "No running timers"
        sys.exit()
    
    print text
    if not prompt:   
        return
    
    if rm is None:
        val = raw_input('Enter a number to delete timer. Or press any key to exit: ')
    else:
        val = rm
    
    if len(val) == 0:
        print ''
        sys.exit()
    
    try:
        val = int(val)
        try:
            file = iname[val]
        except KeyError:
            print "Invalid timer number"
            sys.exit(2)
        
        os.remove('/var/tmp/timer/' + file)
        print 'Removed Timer {:d}'.format(val)
        sys.exit()
    except ValueError:
        print "Invalid Entry"
        sys.exit(2)
    

def _settimer(t,m=''):

    FNULL = open(os.devnull, 'w')
    
    selfPath = os.path.abspath(__file__)
    cmd = 'nohup nice python {:s} _run {:0.10f} {:s}'.format(selfPath,t,m)
    
    subprocess.Popen(cmd.split(),stdout=FNULL, stderr=subprocess.STDOUT)
    print _gettxt(t,m)    

def _gettxt(t,m='',ret_end=False):
    start = datetime.now()
    end0 = start + timedelta(minutes=t) 
    
    start = start.strftime(fmt)
    end = end0.strftime(fmt)
    
    txt = 'Time: {:0.2f} min, Start: {:s}, End: {:s}'.format(t,start,end)
    if len(m) > 0: 
        txt += ', Message: {:s}'.format(m)
    if not ret_end:
        return txt
    else:
        return txt,end0

def _runtimer(t,m=''):
    """ 
    Set a timer for t. The code will write a timer file before sleeping
    and then look for it when it wakes up. If it has been deleted, nothing
    happens (essentially, the timer is canceled). Deleting a timer does NOT
    end the process but it silences it.
    
    Name of the timer is the end time in unix time
    """
    t = float(t) # minutes
    
    if not os.path.exists('/var/tmp/timer'):
        os.makedirs('/var/tmp/timer')
    
    txt,endobj = _gettxt(t,m,ret_end=True)
    
    name = '/var/tmp/timer/' + str(time.mktime(endobj.timetuple()))
    with open(name,'w') as F:
        F.write(txt)
        
    time.sleep(t*60)
    
    if not os.path.exists(name):
        return # It was deleted while sleeping
    else:
        os.remove(name)
    
    # Just mac for now. Will add linux later
    uname = os.uname()[0]
    if uname.lower() == 'darwin':
        cmd = """terminal-notifier -message 'Timer Finished: {:0.2f} minutes. {:s}' -title 'Timer'""".format(t,m)
        os.system(cmd)
        os.system('say -v bells "beep"')
    

if __name__=='__main__':
    """ Crude interface. No need for getopt,etc """
    
    if len(sys.argv) == 1:
        mode = 'list'
    else:
        mode = sys.argv[1]
    
    mode = mode.replace('-','').strip() # For flags such as -h
    
    t = None
    try:
        t = float(mode)
        mode = '_time'
        m = ''
        if len(sys.argv)>2:
            m = ' '.join(sys.argv[2:])
    except ValueError:
        assert mode.lower() in ['h','help','list','manage','_run','_time','delete'],"Not a mode"
    
    mode = mode.lower()
    if mode == '_run':
        t = float(sys.argv[2]) # Will error if not specified
        m = ''
        if len(sys.argv)>3:
            m = ' '.join(sys.argv[3:])
    
    # Modes!
    if mode in ['_run']:
        _runtimer(t,m)
        sys.exit()
    if mode in ['_time']:
        _settimer(t,m)
        sys.exit()
    elif mode in ['h','help']:
        print(usage())
        sys.exit()
    elif mode in ['manage','delete']:
        if len(sys.argv) > 2:
            _manage(True,sys.argv[2])
        else:
            _manage(True)
    elif mode in ['list']:
        _manage(False)
    



    
     
    
    
