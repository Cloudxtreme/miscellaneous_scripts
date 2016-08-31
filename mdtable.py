#!/usr/bin/env python
""" Create pretty Markdown (pipe) tables """
import sys
import getopt

usage_short="""
    Cleanup piped (or file) contents to a prettier table for Markdown
    
    Usage: Tip: add `alias mdtable='python /path/to/mdtable.py'` to your profile
      
      <input>  | python [options] mdtable.py

    See `mdtable.py -H` for more
    
    Written by Justin Winokur, 2016-06
    """

usage="""
  Cleanup (default) or convert input to nicer table
  
  Usage: Tip: add `alias mdtable='python /path/to/mdtable.py'` to your profile
  
    <input>  | python [options] mdtable.py
  
  Options (`=` means requires input):
      -c,--csv
          Processes the txt as comma separated values. Ignore relevant 
          other options
      
      -d=,--delimiter=  
          ['|'] Set the delimiter. Default just cleans up a table. 
          Enter as `-d "|"` so as to not pipe output. NOTE: If using a 
          space as the delimiter, empty center columns will be removed.
              Tip: Put "_" where you want an empty space and then remove
                   it manually       
      
      -f=,--file=
          Read from a file instead of stdin
      
      -h
        Short help
        
      -H,--help
          Print this help
      
      -n,--no_head
          Do not make the first row a header row. If the code detects a row 
          that is just `|`,`-`,`:`, it will assume that there is a header on
          the input, remove that row, and ignore the `--no_head` flag.
          
          If not header row, a blank row (`|  |  |`, etc) will be used
      
      -o=,--out-file=
          Specify an output file rather than printing it to screen 
          (or piping/redirecting)
      
      -s,--start_end
          Do NOT print starting and ending `|` on each line
  
  Suggested Usage and Tips:
      
      * Format clipbord (on a Mac)
          pbpaste | mdtable | pbcopy
      * Alias adjusting clipboad 
          `alias cbmd='pbpaste|python /path/to/mdtable.py|pbcopy'`
  Notes:
      *   This DOES NOT support alignment options with `:`. Add them later
      *   Rows with fewer columns than the longest row will have columns added
          at the end. Add delimiters to adjust accordingly. (see notes above 
          for spaces as delimiters)
      *   There is also a Python tools called tabulate that can do some of this
          with more formats but this one only needs the standard library
    
    Examples:
        Input:
            
            a|b|c
            first | | <-- empty
            |<--empty-->
            normal | normal | normal    
        
        Output: <input text> | mdtable
        
            | a      | b           | c         |
            |--------|-------------|-----------|
            | first  |             | <-- empty |
            |        | <--empty--> |           |
            | normal | normal      | normal    |

        Output: <input text> | mdtable -n        
            |        |             |           |
            |--------|-------------|-----------|
            | a      | b           | c         |
            | first  |             | <-- empty |
            |        | <--empty--> |           |
            | normal | normal      | normal    |

        Output: <input text> | mdtable -s

             a      | b           | c
            --------|-------------|-----------
             first  |             | <-- empty
                    | <--empty--> |
             normal | normal      | normal
    
    Written by Justin Winokur, 2016-06

"""

def make_table(txt,delimiter='|',header=True,csv=False,startend=True):

    output = []

    # Add a space before each new line and at EOF for compatability
    txt = txt.replace('\n',' \n ') + ' '
    
    if csv:
        import csv
        table = [row  for row in csv.reader(txt.split('\n'))]
    else:    
        # Clean delimiter but add back a space if it is then empty
        delimiter = delimiter.strip()
        if len(delimiter) == 0:
            delimiter = ' '
    
        table = [x.split(delimiter) for x in txt.split('\n')]

    # Clean it up
    
    table = [ [col.strip() for col in row] for row in table]  # Remove spaces
    table = [row for row in table if not (len(row) == 1 and len(row[0])==0)] # Remove empty rows
    
    # Clean up for " " delimiter
    if delimiter == ' ':
        table = [ [col for col in row if len(col)>0] for row in table] # Remove empties
    
    # Number of columns per row
    ncol = max([len(row) for row in table])
    
    # Append empty columns for shorter rows
    table = [row + ['']*(ncol-len(row)) for row in table]
    
    # Remove the header row before doing any other calculations
    # Look at just the second row (table[1]). See if it already a header
    isHead = lambda entry: all([digit.strip() in '-:' for digit in entry])
    
    hasHeader = False
    if len(table) > 1:
        hasHeader = all( [isHead(entry) for entry in table[1]] ) # Are all of the entries for the second row headers?

    if hasHeader:
        del table[1]
        header = True

    # strip the output of each cell
    table = [ [col.strip() for col in row] for row in table]

    # Get the largest length of each column
    col_length = [[len(col) for col in row] for row in table] # all columns
    col_length = [max(i) for i in zip(*col_length)] # maximum

    # Remove the first and/or last column(s) if its length is zero. 
    # length zero middle columns are not removed.
    while col_length[0] == 0:
        table = [ [col for col in row[1:]] for row in table]
        col_length = col_length[1:]
    while col_length[-1] == 0:
        table = [ [col for col in row[:-1]] for row in table]
        col_length = col_length[:-1]

    ########## At this point the table is nicely cleaned up. Printing below:

    # Make a new table with each entry being spaced uniformly
    table = [  [' ' + col.ljust(col_length[nc]) + ' ' for nc,col in enumerate(row)] for row in table] 

    se = ''
    if startend:
        se = '|'

    # Make the table
    for irow,row in enumerate(table):
        # Make and print the empty header if no header
        if irow == 0 and not header:         
            empt = [' '*len(col) for col in row]
            dash = ['-'*len(col) for col in row]
            output.append(se + '|'.join(empt) + se)
            output.append(se + '|'.join(dash) + se)
        
        output.append(se + '|'.join(row) + se)    
    
        # Make and print the header
        if irow == 0 and header:         
            dash = ['-'*len(col) for col in row]
            output.append(se + '|'.join(dash) + se)
 
    
    output = '\n'.join(output)
    
    return output
    
    
if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cd:f:Hhno:s", ["csv", "file=","delimiter=","help","no_head","output=","start_end"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print "\n Printing (short) Help:\n"
        print(usage_short)
        sys.exit(2)
  
    ## Process the options
    # Defaults
    csv = False
    delimiter = '|'
    Header = True
    startend = True
    file = None
    outFile = None
    
    
    for  o,a in opts:
        if o in ("-c","--csv"):
            csv = True
        if o in ("-d", "--delimiter"):
            delimiter = a
        if o in ['-f','--file']:
            file = a
            if file.startswith('='):
                file = file[1:]
        if o in ("-H","--help"):
            print(usage)
            sys.exit()
        if o in ('-h'):
            print(usage_short)
            sys.exit()
        if o in ("-n","--no_head"):
            Header = False
        if o in ['-o','--out-file']:
            outFile = a
            if outFile.startswith('='):
                outFile = outFile[1:]
        if o in ("-s","--start_end"):
            startend=False
    
    if sys.stdin.isatty() and file is None: # does it have input
        sys.exit()
    
    if file is None:
        txt = sys.stdin.read()
    else:
        with open(file,'r') as F:
            txt = F.read()
    
    output = make_table(txt,delimiter=delimiter,header=Header,csv=csv,startend=startend)
    
    if outFile is None:
        print(output)
    else:
        with open(outFile,'w') as F:
            F.write(output)




















