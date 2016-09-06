#!/usr/bin/env bash

###########################################################################
########################### Dated Backup Script ###########################
###########################################################################
#     Create Time-Machine like backups from the specified
#     source to the destination
#     
#     Usage:
#         * Set up paths below
#         * Run the code
#             ./dated_backup.sh
#     
#     Description:
#         Will create a time-machine like backup structure where only *new*
#         files are backed up. However, if you navigate to each directory,
#         you will see the *full* file-system of the source
#         
#         This is done with hardlinks. An advantage of this is that you 
#         can delete the file in any directory without affecting the linked
#         files.
#     
#     Tips / Notes:
#         * Some OSes do not correctly report the size used due to the hard-
#           links. To see the size, navigate to the backup destination and
#           run
#         
#               du -sch *
#         
#           to see the actual sizes
# 
#         * If you're running this in cron, add '>/dev/null 2>&1' (w/o quotes)
#           to the end     
#         
#         * It is 100% safe to delete any backup directory except 
#             - 'current' and
#             - the latest dated backup
#           To delete them, use 'rm -rf backup[...]' but do so at your own risk
# 
#     Based on
#       http://blog.interlinked.org/tutorials/rsync_time_machine.html
#       http://blog.interlinked.org/tutorials/rsync_addendum.yaml.html
# 
#     modified and adjusted by Justin Winokur,
#     2016-06
###########################################################################

# Specify the source directory
source_dir=/path/to/source/dir

# Specify the backup destination
back_dest=/path/to/destination/dir

# Specify how to prefix the backups
back_pre='backup'

###########################################################################
###########################################################################

# Make sure the source path ends in a `/`
if [ "${source_dir: -1}" != "/" ]; then
    source_dir=$source_dir"/"
fi

# Make sure the dest path does not ends in a `/`
if [ "${back_dest: -1}" = "/" ]; then
    back_dest="${back_dest%?}"
fi

# Is this the first time
if [ ! -d "$back_dest/current" ]; then
    echo "--- Initial Run ---"
    rsync -aPE --stats $source_dir $back_dest/current 
    echo "-------------------"
fi

date=`date "+%Y-%m-%dT%H_%M_%S"`

rsync -aPEHh --stats \
    --link-dest=$back_dest/current \
    $source_dir $back_dest/$back_pre-$date

rm -rf $back_dest/current

ln -s $back_dest/$back_pre-$date \
    $back_dest/current











