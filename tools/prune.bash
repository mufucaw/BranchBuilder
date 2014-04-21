#!/bin/bash
build_dir="/var/www/public/builds"
cd $build_dir
cwd=`pwd`
if [ "$cwd" = "$build_dir" ];then
    find . -maxdepth 1 ! -path . -type d -mtime +14 -exec rm -rf {} \;
fi

prune_tool="/var/www/BranchBuilder/tools/PruneBuildsTask.py"
if [ -f $prune_tool ];then
python $prune_tool
fi


