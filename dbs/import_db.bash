#!/bin/bash
db_name="branchbuilder.new.20130707"
schema="schema_20150409.sql"
sqlite3 $db_name < $schema
for x in `sqlite3 $db_name ".tables"` ; do
sqlite3 $db_name << !    
.mode list
.header on
.separator |
.import $x.csv $x
!
done
