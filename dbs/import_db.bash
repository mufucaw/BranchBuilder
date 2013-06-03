#!/bin/bash
for x in `sqlite3 branchBuilder.bak.20130602 ".tables"` ; do
sqlite3 branchbuilder.sqlite3 << !    
.separator ,
.mode csv
.import $x.csv $x
!
done
