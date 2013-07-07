#!/bin/bash
db_name="branchbuilder.new.20130707"
for x in `sqlite3 $db_name ".tables"` ; do
sqlite3 $db_name << !    
.separator ,
.mode csv
.import $x.csv $x
!
done
