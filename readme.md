# Miscellaneous Scripts

Collection of scripts I have written or adapted.

Some scripts are aliased (for example, `agit` for `allgit.sh`) while others are sourced.

Each script is self-contained (mostly) with details on usage.

Most are designed for either Mac (BSD) or Linux, though a few are specific.

**Use at your own risk**


## Scripts

### `allgit.sh`

(Usually aliased as `agit`). Perform the same git command in all subdirectores that are git repos (default depth 1 but is adjustable). Useful for managing many repos at once. There are more advanced solutions but this is just simpler

### `autoMD.py` (and `autoMD_CSS.css`)

Markdown-previewer with auto-refresh. If you're on a mac, use [Marked2App](http://marked2app.com/) since it is better in just about every way possible. This tool is good for when you do not have a mac and/or you can not install something yourself. 

Also, pretty bad coding style! (but hey, it works)

### `cleanExportNB.py`

Adapted from <https://gist.github.com/minrk/6176788>. Clears up Jupyter/IPython notebooks and also does an export.

I like to put the following in my `.bash_profile` for this:

    cleanExportNBall() {  
        find . -name "*.ipynb" -type f -print0 |xargs -0 -I {} /path/to/cleanExportNB.py {}; 
    }
    alias cleanExportNB='/path/to/cleanExportNB.py'

### `fgrep.py`

**f**ile **grep** -- Wrapper to grep files since I tend to easily forget the commands. Honestly, not all that useful if you remember things, but I tend to forget this one.

The biggest help this can be is to do better `AND` searching by making all permutations of the input parameters.

See documentation inline for example

### `gitpath.py`

Parses git info on files and print the hash and commit date. Also can print with `-f` for lots more information. The idea is that this should be enough information to recover the exact file no matter what (dates are good in case hashes change with rebase,etc)

### `mdtable.py`

Prettify markdown pipe-tables and/or convert with other delimiter.

For example:

    A , B, C, D
    1,2,3333
    a,b,,skipped `c`

with `<cat or echo or paste the above> | mdtable -d ","`:

    | A | B | C    | D           |
    |---|---|------|-------------|
    | 1 | 2 | 3333 |             |
    | a | b |      | skipped `c` |


### `timer.py`

Create a background timer that can also be managed. The basics are mac/linux but at the moment, I only have notifications for mac set up.

































