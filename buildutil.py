import re
import urllib2
import os

import web
from jenkins import Jenkins
from jinja2 import Template
import appconfig

class JobBuilder:

  def __init__(self, jenkinsURL):
    self.j = Jenkins(jenkinsURL)
    self.jobName = ""

  def add_job(self, jobName, configString):
    self.jobName = jobName

    if self.j.job_exists(jobName):
      #Job exist in the job list
      return False
    else:
      self.j.create_job(self.jobName, configString)
      self.j.enable_job(self.jobName)

      return True

  def run_job(self, **params):
    if self.jobName == "":
      print "Have to add job firstly"
      return False
    else:
      self.j.enable_job(self.jobName)
      self.j.build_job(self.jobName, params)

class TaskBuilder:

  def __init__(self, jenkinsURL):
    self.j = Jenkins(jenkinsURL)
    self.jobName = ""
    #with open("config.xml") as file:
    with open("./builds/config/job/config.xml") as file:
      self.templateConfig = file.read()
    self.template = Template(unicode(self.templateConfig))

  def set_new_config(self, **params):
    self.newConfig = self.template.render(repos=params['repos'], description=params['repos'])

  def add_build(self, **params):
    self.set_job_name(**params)
    self.set_new_config(**params)

    if self.j.job_exists(self.jobName):
      self.do_build(**params)
    else:
      
      self.j.create_job(self.jobName, self.newConfig)
      self.do_build(**params)

  def do_build(self, **params):
    self.set_job_name(**params)
    self.set_new_config(**params)

    self.j.enable_job(self.jobName)
    self.j.build_job(self.jobName, {'branch': params['branch'], 'version': params['version'], 'author': params['author'], \
      'styleguide_repo': params['styleguide_repo'], 'styleguide_branch': params['styleguide_branch'], 'sidecar_repo': params['sidecar_repo'], \
      'sidecar_branch': params['sidecar_branch'], 'package_list': params['package_list'], 'upgrade_package': params['upgrade_package'], \
      'latin': params['latin'], 'demo_data': params['demo_data']} )
  
  def set_job_name(self,**params):
    buildUtil = BuildUtil()
    self.jobName = buildUtil.get_job_name(repos=params['repos'])

  def get_build_status(self, jobName):
    #job_info = self.j.get_job_info(self.jobName)
    #return build_status
    color_status = {"aborted":"Aborted",  "red": "Failed", "blue": "Succcess"}
    if jobName == "":
      print "Have to specify job name"
      return False
    else:
      if self.j.job_exists(jobName):
        #Job exist in the job list
        job_info = self.j.get_job_info(jobName)

        if color_status.has_key(job_info['color']):
          return color_status[job_info['color']]
        else:
          return 'Running'
      else:
        print "Have to specify a validate job name"
        return False

  def get_job_name(self):
    return self.jobName

  def stop_jenkins_job(self, job_url):
    """
    1. stop one job
    """
    stop_job_url = job_url + 'lastBuild/stop'
    try:
      ss = urllib2.urlopen(stop_job_url, None, 30).read()
      ss.close()
    except:
      return '{}'

  def stop_jenkins_jobs(self, jobName):
    """
    1. find all the sub job
    2. stop all the running sub job
    3. stop current job
    """
    if self.j.job_exists(jobName):
      for x in self.j.get_job_info(jobName)['downstreamProjects']:
        if self.get_build_status(x['name']) == 'Running':
          self.stop_jenkins_job(x['url'])
      self.stop_jenkins_job(self.j.get_job_info(jobName)['url'])
    else:
      pass

class BuildUtil:
  def __init__(self):
    pass
  
  def get_md5(self, string):
    try:
      import hashlib
      md5_str = hashlib.md5(string).hexdigest()
    except Exception:
      import md5
      md5_str = md5.md5(string).hexdigest()

    return md5_str

  def get_job_name(self, **params):
    return 'Build' + '_' + self.get_md5(params['repos'])

  def sanitize_input(self, i):
    """Strips whitespace from input, returns dict"""
    for item in i:
      i[item].strip()
    return i

  def determine_styleguide_branch(self, styleguide_repo, styleguide_branch, version):
    """Returns styleguide branch name with version included if submitted values are default"""
    # hardcoded defaults... The following if statement really should check the default values in the template file
    if styleguide_repo == "git@github.com:sugarcrm/styleguide.git" and styleguide_branch == "master":
      updated_branch = "%s_%s" % (styleguide_branch, version.replace(".", "_"))
      updated_branch = re.sub(r"(.*)\_0$", r"\1", updated_branch)
      return updated_branch
    else:
      return styleguide_branch

  def generate_user_name(self, full_name):
      full_name = full_name.replace(".", "")
      full_name = full_name.replace("#", "")
      full_name = full_name.replace("_", "")
      full_name = full_name.replace("-", "")
      if full_name == "":
          return ""
      else:
          full_name_list = full_name.split(" ")	
          if len(full_name_list) > 1:
              user_name = full_name_list[0][0] + full_name_list[-1]
          else:
              user_name = full_name_list[0]
  
      return user_name[0:16].lower()

  def get_build_number(self, build):
      build_number = ""
      build['username'] = self.generate_user_name(build['author'])
      builds_dir = os.path.realpath(appconfig.builds_dir)
      if os.path.exists(builds_dir + "/" + build['username']
                        + build['branch'] + '/latest'):
          build_number = os.readlink(builds_dir + "/"
                  + build['username'] + build['branch']
                  + '/latest')

      return build_number
