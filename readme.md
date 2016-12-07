# Miscellaneous Scripts

Collection of scripts I have written or adapted.

Some scripts are aliased but others are intended to be in your path
(For example, I intentionaly like to do `alias timer="timer.py"` to prevent issues on some machines, but `agit` and `git-path` are in the bash path)

Each script is self-contained (mostly) with details on usage.

Most are designed for either Mac (BSD) or Linux, though a few are specific.

**Use at your own risk** (though I haven't had a problem)


## Scripts

### `agit`

(Usually aliased as `agit`). Perform the same git command in all subdirectores that are git repos (default depth 1 but is adjustable). Useful for managing many repos at once. There are more advanced solutions but this is just simpler

### `autoMD` (and `autoMD_CSS.css`)

Markdown-previewer with auto-refresh. If you're on a mac, use [Marked2App](http://marked2app.com/) since it is better in just about every way possible. This tool is good for when you do not have a mac and/or you can not install something yourself. 

Also, pretty bad coding style! (but hey, it works)

### `cd_commands.sh`

(intended to be `source /path/to/cd_commands.sh` in `.bash_profile`). Function to overwrite `cd` to use `pushd` (and `popd` if you change the comments). 

### `cleanExportNB.py`

Adapted from <https://gist.github.com/minrk/6176788>. Clears up Jupyter/IPython notebooks and also does an export.

I like to put the following in my `.bash_profile` for this:

    cleanExportNBall() {  
        find . -name "*.ipynb" -type f -print0 |xargs -0 -I {} /path/to/cleanExportNB.py {}; 
    }
    alias cleanExportNB='/path/to/cleanExportNB.py'

### `dated_backup.sh`

Shell script that works makes a Time Machine like backup. It uses `rsync` and hard-links to make a full-folder system backup but only use space for the new files. You need to manually purge older backups but that can be done safely.

Excludes, etc should be specified in the rsync calls (I should add them...)

Based on [this][ilink1] and [this followup][ilink2].

[ilink1]:http://blog.interlinked.org/tutorials/rsync_time_machine.html
[ilink2]:http://blog.interlinked.org/tutorials/rsync_addendum.yaml.html

### `fgrep`

**f**ile **grep** -- Wrapper to grep files since I tend to easily forget the commands. Honestly, not all that useful if you remember things, but I tend to forget this one.

The biggest help this can be is to do better `AND` searching by making all permutations of the input parameters.

See documentation inline for example

### `git-path`

Parses git info on files and print the hash and commit date. Also can print with `-f` for lots more information. The idea is that this should be enough information to recover the exact file no matter what (dates are good in case hashes change with rebase,etc)

Note: if you call `git path`, git will automatically call `git-path`

### `git-stat`

If using a newer version of it, simple a shortcut to `git status --short --branch` but if using an older version (I don't always get a choice...), uses Python to replicate *some* of the `--branch` features

Note: calling `git stat` is the same as `git-stat`

### `history_commands.sh`

(intended to be `source /path/to/history_commands.sh` in `.bash_profile`). Commands to change the way history is reported and/or stored. Most useful (in my opinion) is `pwd2hist` which puts the current directory in history and then `hist` which gives you the last few history commands.


### `mdtable`

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

































