#!/usr/bin/env python
"""
Code to autocompile Mardown. Hacked together with lots of (bad) global
variables, but it works

Also supports mathjax but ONLY if the environmental variable `MATHJAX` is set

Tips: 
    * Set `export MATHJAX='/local/path/to/MathJax.js'` in your bash profile for
      local install
    * Set `export MATHJAX='https://cdn.mathjax.org/mathjax/latest/MathJax.js'
      for hosted version
"""


import markdown
import os
import re


usage="""

autoMD.py  -- Automatically compile MD to a page and open it

Options: 
  `=` requires input
  Conflicting options will use the latest specified

    -h,--help
        Display this help page
    -m,--manual
        No automatic refresh of HTML page
    -n,--no-open
        Does not open the page upon complie.
    -o=,--out-file=
        Specify an output file location. Default is a tmp file
    -r=,--refresh=
        [5] Specify the auto-refresh rate of the page in seconds. 
        Use `-m` for no refresh
    -s,--single
        Single mode. Compiles and opens. Overides `-r` and `-m`. Does NOT
        override `-n`
    -t=,--polling=
        [1] Specify the time between polling for an updated file

Tips:
    * Use an alias to make easier
    * alias `md` (or whatever you want) to `-s` mode
    
"""



reIMG = re.compile('\<img.+?src=".+?".*?\>',re.IGNORECASE)
retoc = re.compile('^\ {0,3}\[TOC\]|\n\ {0,3}\[TOC\]|^\ {0,3}\{\{TOC\}\}|\n\ {0,3}\{\{TOC\}\}') # new line or start of line, 0-3 leading spaces


def MMDcompile(textIn):
    """
    compile
    """
    textIn = textIn.replace('\n','   \n') # add spaces at the end of each line
    try:
        textIn = unicode(textIn, "utf-8")
    except:
        pass
    
    if len(retoc.findall(textIn)) >0:
        textIn = retoc.sub('\n[TOC]',textIn) # Replace `{{TOC}}` with `[TOC]`
        # If ever using a different Markdown code, this is where to make the 
        # replacement for new TOC
    
    
    html = markdown.markdown(textIn, ['markdown.extensions.extra','markdown.extensions.toc'])
    return html
    
def fixPath(path):
    if path.endswith('/'):
        return path
    return path + '/'
        
def comp(file):
    global outPath,refresh
    global lastDate,moddate
    global title
    
    dict = {'{title}':title}

    with open(file,'r') as F:
        content = F.read()

    toptxt = '`autoMD.py` - Modification Date: {0:s}, Last Compiled: {1:s}. '.format(\
        moddate.strftime('%Y-%m-%d %H:%M:%S'),lastDate.strftime('%Y-%m-%d %H:%M:%S'))
    if refresh is None:
        if not singleMode:
            toptxt +='Must refresh manually'
    else:
        toptxt +='Will auto-refresh every {0:0.2f} seconds'.format(refresh)
    
    toptxt = MMDcompile(toptxt+'\n\n')
    bottomtxt=MMDcompile('\n\n------\n\n<small>autoMD Note: Internal image destinations are updated but links may not work</small>')
    
    dict['{top}'] = toptxt
    dict['{bottom}'] = bottomtxt
    dict['{refresh}'] = ''
    if refresh is not None:
        dict['{refresh}'] = '<meta http-equiv="refresh" content="{0:f}">'.format(float(refresh))
    
    dict['{content}'] = imgRoot(MMDcompile(content),file)
    dict['{csspath}'] = __file__.replace('autoMD.py','autoMD_CSS.css')
    dict['{mathjax}'] = MathJaxHeader()
    
    
    html = template
    for key,val in dict.items():
        html = html.replace(key,val)
    
    #outPath = fixPath(outPath)
    with open(outPath,'w') as F:
        F.write(html.encode('utf8'))

def imgRoot(content,file):
    """
    Add the absolute path to all images
    
    Heuristic based. May not be perfect
    
    """
    basePath = os.path.split(os.path.abspath(file))[0]  + '/'

    repDict = {}
    
    for image in reIMG.findall(content):
        srcIX = image.find('src="')
        srcIXe = image.find('"',srcIX+5)
        link = image[srcIX+5:srcIXe]
        if any([link.startswith(a) for a in ['/','~/','http://','https://','file://']]):
            continue
        newlink = basePath + link
        
        # replace the link part of image and 
        newImage = image.replace('src="'+link,'src="'+newlink)
        repDict[image] = newImage
    
    for a,b in repDict.items():
        content = content.replace(a,b)
    
    return content
    

##########################################
"""

This is a boiler-plate code to automatically perform an action when `path` 
changes. The action is in the part called `Update Here` except for `timeout` 
which is set below. This value is how many seconds to wait before polling the 
file. A low value is NOT suggested. Suggested values are 0.25 to 1.0

"""


import sys,os,time
from datetime import datetime
from select import select

def autofill(path):
    global outPath,refresh,pageOpen
    global lastDate,moddate
    lastDate = datetime(1900,1,1)
    print('   Watch and Compile path:')
    print '    ' + path
    
    firstRun = True
    
    run = True
    
    while True:
        moddate,lastPath = modification_date(path)
        if  moddate > lastDate:
            print 'Last Updated: %s' % moddate.strftime('%Y-%m-%d %H:%M:%S')
            
            ####################################################################
            ########################### Update Here ############################
            if os.path.isdir(path):
                print 'Compiling Folder: {:s}'.format(path)
                print '     Last Updated File: {:s}'.format(lastPath)
            else:
                print 'Compiling File: {:s}'.format(path)
            lastDate = moddate
            comp(lastPath)
            
            ####################################################################
            
            if firstRun:
                firstRun=False
                print "  Output in {0:s}".format(outPath)
                if refresh is None:
                    print "  Must refresh page manually (see options to change)"
                else:
                    print "  Page refreshes ever {0:0.2f} seconds".format(refresh)
                opath = os.path.abspath(outPath)
                if pageOpen:
                    try:
                        import webbrowser
                        webbrowser.open_new_tab('file://'+opath)
                        print "  Page automatically opened"
                    except:
                        print '  Error opening page. Must navigate manually'
                        print '    file://'+opath
                else:
                    print '  Must navigate manually (see options for auto-open)'
                    print '    file://'+opath                    
            else:
                if refresh is None:
                    print "  Must refresh page manually (see options to change)"
            if singleMode:
                break
            
            print "Enter 'X' break (or CTRL+C)"
            
        # End compile loop
        
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        
        if rlist:
            s = sys.stdin.readline()
            if s.lower()[0] == 'x':
                break
            else:
                print "Invalid Entry\nEnter 'X' break (or CTRL+C)"


def modification_date(inpath):
    """
    Get the mod date and path of the inpath
    
    If inpath is a file, just the date and path is inpath
    
    Otherwise, find the latest
    
    """
    if os.path.isdir(inpath):
        t = 0.0
        outpath = ''
        for dirpath, dirnames, filenames in os.walk(inpath):
            # Remove all hidden directories
            for dir in dirnames:
                if dir.startswith('.'):
                    dirnames.remove(dir)
                
            for file in filenames:
                if not file.endswith('.md') or file.endswith('.mmd'):
                    continue
                
                fullFile = os.path.join(dirpath,file)
                tt = os.path.getmtime(fullFile)
                if tt>t:
                    t = tt
                    outpath = fullFile    
    else:
        outpath = inpath
        t = os.path.getmtime(outpath)
        
            
    return datetime.fromtimestamp(t),outpath

def MathJaxHeader():
    """
    Return Mathax text if variable is set
    """

    text = """\
<script type="text/javascript" src="{mathjaxpath}?config=TeX-AMS-MML_HTMLorMML">
</script>
<script type="text/x-mathjax-config">  
MathJax.Hub.Config({  
                    "HTML-CSS": {  
                        messageStyle: "normal",  
                        linebreaks: {  
                            automatic: false  
                        }  
                    },  
                    tex2jax: {   
                        inlineMath: [["$","$"],["\\(","\\)"]],   
                        displayMath: [["$$","$$"],["\\[","\\]"]],   
                        processEscapes: true  
                    },  
                    TeX: {  
                        Macros: {    
                        }  
                    }  
                }  
                );  
</script> 
"""
    if 'MATHJAX' in  os.environ.keys():
        return '\n'+text.replace('{mathjaxpath}',os.environ['MATHJAX'])
    else:
        return ''

def _hash(s):
    import hashlib
    return hashlib.sha1(s).hexdigest()[:8]




template="""\
<!DOCTYPE html>
<html>
<head>
{refresh}
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AutoMD: {title}</title>
<link type="text/css" rel="stylesheet" href="{csspath}">{mathjax}
</head>

<body>
<p>{top}</p>
<hr>
{content}

<p>{bottom}</p>


</body>
</html>
"""
# Template has:
#     {top}       - Top line with info about compile 
#     {content}   - Actual content
#     {refresh}   - Goes in the HEAD. Whether or not to refresh content
#     {title}     - Page title
#     {csspath}   - Path to CSS
#     {bottom}    - Text at the bottom
#     {mathjax}   - Insert Mathjax config if the variable is set
#                   Note that it is not given its own line in case it isn't set





import getopt

if __name__ == '__main__':
    

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hmno:r:st:", ["help","manual","no-open","out-file=","refresh=","single","polling="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print "\n Printing Help:\n"
        print(usage)
        sys.exit(2)
  
    ## Process the options
    # Defaults
    pageOpen = True
    outPath = None
    refresh = 5.0
    timeout = 1.0
    singleMode = False
    
    for  o,a in opts:
        if o in ("-h","--help"):
            print(usage)
            sys.exit()
        if o in ("-m","--manual"):
            refresh = None
        if o in ('-n','--no-open'):
            pageOpen = False
        if o in ("-o","--out-file"):
            outPath = a
        if o in ("-r","--refresh"):
            refresh = float(a)
        if o in ('-s','--single'):
            singleMode=True
        if o in ('-t','--polling'):
            timeout = float(a)
    
    if len(args) == 0:
        print("Must specify a file")
        sys.exit(2)
    
    file = args[0]
    
    if os.path.isdir(file) and file.endswith('/'):   # For the sake of the fileName, remove trailing /
        file = file[:-1]
    
    fileName = os.path.split(file)[-1]
    
    title = fileName
    
    if outPath is None: # Not specified
        outPath = '/tmp/autoMMDout.{:s}.html'.format(_hash(fileName))

    if singleMode:
        refresh = None
        # timeout won't matter because of the break statement
    
    autofill(file)






























