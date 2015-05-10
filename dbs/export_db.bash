#!/bin/bash
db_name="branchbuilder.20130707"
for x in `sqlite3 $db_name ".tables"` ; do
sqlite3 $db_name  << !    
.mode list
.separator |
.header on
.output $x.csv
select * from $x;
!
done
