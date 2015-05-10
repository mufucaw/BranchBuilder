#!/bin/bash
for x in `mysql -usugarbuild -ptest -e "show databases"` ; do
echo $x | grep -q -E "^(ult)|(ent)|(corp)|(pro)|(ce)"
status=$?
	if [ 0 == $status ] && [ $x != "mysql" ]; then
	echo $x
	echo $x >> drop_db.log
	mysqladmin -f -uroot -psugarcrm drop $x
	fi
done
