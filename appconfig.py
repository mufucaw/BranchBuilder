site_url='http://honey-g/BranchBuilder'
jenkins_url='http://honey-g:8080'
od_users = {
		"anisevich": {"full_name": "Alex Nisevich", "email": "anisevich@sugarcrm.com"} ,\
		"betauser1": {"full_name": "Beta User1", "email": "quality-assurance@sugarcrm.com"} ,\
		"betauser2": {"full_name": "Beta User2", "email": "quality-assurance@sugarcrm.com"} ,\
		"cfox": {"full_name": "Chinghua Fox", "email": "cfox@sugarcrm.com"} ,\
		"cyan": {"full_name": "Carmen Yan", "email": "cyan@sugarcrm.com"} ,\
		"dclunie": {"full_name": "David Clunie", "email": "dclunie@sugarcrm.com"} ,\
		"dsafar": {"full_name": "David Safar", "email": "dsafar@sugarcrm.com"} ,\
		"egan": {"full_name": "Emily Gan", "email": "egan@sugarcrm.com"} ,\
		"eyang": {"full_name": "Eric Yang", "email": "eyang@sugarcrm.com"} ,\
		"franklin": {"full_name": "Fanklin Liu", "email": "franklin@sugarcrm.com"} ,\
		"jimmy": {"full_name": "Jimmy Chen", "email": "jchen@sugarcrm.com"} ,\
		"gpatterson": {"full_name": "Geno Patterson", "email": "gpatterson@sugarcrm.com"} ,\
		"grelampagos": {"full_name": "Gino Relampagos", "email": "gpatterson@sugarcrm.com"} ,\
		"jchen": {"full_name": "Jackie Chen", "email": "chenj@sugarcrm.com"} ,\
		"jcho": {"full_name": "Jessica Cho", "email": "jcho@sugarcrm.com"} ,\
		"jxia": {"full_name": "Jennifer Xia", "email": "jxia@sugarcrm.com"} ,\
		"mlouis": {"full_name": "Mazen Louis", "email": "mlouis@sugarcrm.com"} ,\
		"oyang": {"full_name": "Oliver Yang", "email": "oyang@sugarcrm.com"} ,\
		"rlee": {"full_name": "Randy Lee", "email": "rlee@sugarcrm.com"} ,\
		"rsennewald": {"full_name": "Ray Sennewald", "email": "rsennewald@sugarcrm.com"} ,\
		"rzhou": {"full_name": "Ran Zhou", "email": "rzhou@sugarcrm.com"} ,\
		"phuang": {"full_name": "Paul Huang", "email": "phuang@sugarcrm.com"} ,\
	}
od_users["tester"] =  {"full_name": "QA Tester", "email": "oyang@sugarcrm.com"}
od_version = ['6.5.9', '6.5.10', '6.5.11', '6.5.12', '6.6.0', '6.6.1', '6.6.2','6.6.3', '6.7.0', '6.7.1']
ci_users = dict(od_users)
ci_version = ['6.7.1']

nomad_users = {
		"builder": {"full_name": "Branch Builder", "email": "build@sugarcrm.com"} , \
	}
nomad_version = ['6.7.1']
nomad_flavors = ['Ult', 'Ent', 'Crop', 'Pro']
