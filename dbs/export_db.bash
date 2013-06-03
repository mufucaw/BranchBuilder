#!/bin/bash
for x in `sqlite3 branchBuilder.bak.20130602 ".tables"` ; do
sqlite3 branchBuilder.bak.20130602 << !    
.mode list
.separator |
.output $x.csv
select * from $x;
!
done
