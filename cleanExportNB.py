#!/usr/bin/env python
"""strip outputs from an IPython Notebook
Opens a notebook, strips its output, and writes the outputless version to the original file.
Useful mainly as a git filter or pre-commit hook for users who don't want to track output in VCS.
This does mostly the same thing as the `Clear All Output` command in the notebook UI.
LICENSE: Public Domain
"""

## JW Note: from https://gist.github.com/minrk/6176788

import io
import sys
import os  

try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current
    
        def read(f, as_version):
            return current.read(f, 'json')
    
        def write(nb, f):
            return current.write(nb, f, 'json')


def _cells(nb):
    """Yield all cells in an nbformat-insensitive manner"""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for cell in ws.cells:
                yield cell
    else:
        for cell in nb.cells:
            yield cell


def strip_output(nb):
    """strip the outputs from a notebook object"""
    nb.metadata.pop('signature', None)
    for cell in _cells(nb):
        if 'execution_count' in cell:
            cell['execution_count'] = None
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'prompt_number' in cell:
            cell['prompt_number'] = None
    return nb


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('No specified Notebook')
        sys.exit(2)
    
    
    filename = sys.argv[1]
    
    if not filename.find('/.') == -1:
        # in a dot-folder
        sys.exit()
    
    with io.open(filename, 'r', encoding='utf8') as f:
        nb = read(f, as_version=NO_CONVERT)
    nb = strip_output(nb)
    with io.open(filename, 'w', encoding='utf8') as f:
        write(nb, f)
    print('Cleaned {:s}'.format(filename))
    
    if not os.path.exists('ipynb_auto_conversion'):
        os.makedirs('ipynb_auto_conversion')
        
    if not ( filename.startswith('/') or filename.startswith('./')): # Relative path. Add to make it split correctly later
        filename = './' + filename
        

    rootPath,fileName2 = os.path.split(filename)
    
    rootPath += '/ipynb_auto_conversion/' # because of the above check, this will always have a non-empty rootPath
    
    if not os.path.exists(rootPath):
        os.makedirs(rootPath)
    
    outPath = rootPath + fileName2
    
    cmd = 'jupyter nbconvert --to python --output {:s}.py {:s}'.format(outPath,filename)
    os.system(cmd)











