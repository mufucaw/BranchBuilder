import logging
logging_setting = {
    "filename" : "logger",
    "level" : logging.DEBUG,
    "format" : '%(asctime)s %(message)s',
    "datefmt" : '%Y-%m-%d %H:%M:%S' 
}

site_url='http://honey-g/BranchBuilder'
jenkins_url='http://honey-g:8080'
per_page = 20
od_users = {
		"anisevich": {"full_name": "Alex Nisevich", "email": "anisevich@sugarcrm.com"} ,\
		"betauser1": {"full_name": "Beta User1", "email": "quality-assurance@sugarcrm.com"} ,\
		"betauser2": {"full_name": "Beta User2", "email": "quality-assurance@sugarcrm.com"} ,\
		"cfox": {"full_name": "Chinghua Fox", "email": "cfox@sugarcrm.com"} ,\
		"cyan": {"full_name": "Carmen Yan", "email": "cyan@sugarcrm.com"} ,\
		"cwang": {"full_name": "Joe Wang", "email": "cwang@sugarcrm.com"} ,\
		"dclunie": {"full_name": "David Clunie", "email": "dclunie@sugarcrm.com"} ,\
		"dsafar": {"full_name": "David Safar", "email": "dsafar@sugarcrm.com"} ,\
		"egan": {"full_name": "Emily Gan", "email": "egan@sugarcrm.com"} ,\
		"eyang": {"full_name": "Eric Yang", "email": "eyang@sugarcrm.com"} ,\
		"franklin": {"full_name": "Franklin Liu", "email": "franklin@sugarcrm.com"} ,\
		"ifleming": {"full_name": "Ian Fleming", "email": "ifleming@sugarcrm.com"} ,\
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
		"support1": {"full_name": "Support 1", "email": "support@sugarcrm.com"} ,\
		"support2": {"full_name": "Support 2", "email": "support@sugarcrm.com"} ,\
		"support3": {"full_name": "Support 3", "email": "support@sugarcrm.com"} ,\
		"support4": {"full_name": "Support 4", "email": "support@sugarcrm.com"} ,\
		"support5": {"full_name": "Support 5", "email": "support@sugarcrm.com"} ,\
		"phuang": {"full_name": "Paul Huang", "email": "phuang@sugarcrm.com"} ,\
	}
od_users["tester"] =  {"full_name": "QA Tester", "email": "oyang@sugarcrm.com"}
od_version = [
    '6.5.9',
    '6.5.10',
    '6.5.11',
    '6.5.12',
    '6.5.13',
    '6.5.14',
    '6.5.15',
    '6.5.16',
    '6.6.0',
    '6.6.1',
    '6.6.2',
    '6.6.3',
    '6.7.0',
    '6.7.0.1',
    '6.7.1',
    '6.7.2',
    '6.7.3',
    '6.7.4',
    '6.7.5',
    '7.0.0',
    '7.0.1',
    '7.0.0RC1',
    '7.0.0RC2',
    '7.0.0RC3',
    '7.1.0',
    '7.1.5',
    '7.1.5RC1',
    '7.1.5RC2',
    '7.2.0'
]
ci_users = dict(od_users)
ci_version = ['6.7.1', '6.7.2', '6.7.3', '6.7.4', '6.7.5', '7.0.0', '7.0.1', '7.1.0', '7.1.5', '7.1.5RC1', '7.1.5RC2', '7.2.0']

nomad_users = {
		"builder": {"full_name": "Branch Builder", "email": "build@sugarcrm.com"} , \
	}
nomad_version = ['6.7.1']
nomad_flavors = ['Ult', 'Ent', 'Crop', 'Pro']
builds_dir = "/var/www/public/builds"
kue_server = "http://honey-g:3000"
