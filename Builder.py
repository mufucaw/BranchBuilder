#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import uuid
import web
from jenkins import Jenkins

import json
import urllib2
import re
from datetime import datetime
import logging
import requests

from buildutil import *
import BuildConfig
import ODDeploy
import CIDeploy
import Nomad
import appconfig
import versionconfig
from models.branchbuilder import BranchBuilder

#init the logging
logging.basicConfig(**appconfig.logging_setting)

render = web.template.render('template/', base='layout')
urls = (
    '/', 'Index',
    '/add', 'Add',
    '/build', 'Build',
    '/buildstatus', 'BuildStatus',
    '/cron', 'BuildCron',
    '/getbuild', 'GetBuild',
    '/stopbuild', 'StopBuild',
    '/searchbuild', 'SearchBuild',
    '/updatebuild', 'UpdateBuild',
    '/remove', 'Remove',
    '/sendmail', 'SendMailToAdmin',
    '/fullview', 'FullView',
    '/logger', 'Logger',
    '/buildconfig', BuildConfig.app_BuildConfig,
	'/mappedversion', 'MappedVersion',
    '/ODDeploy', ODDeploy.app_ODDeploy,
    '/CIDeploy', CIDeploy.app_CIDeploy,
    '/Nomad', Nomad.app_Nomad,
    )

web.config.smtp_server = 'localhost'
web.config.smtp_port = 25
web.config.debug = False
app = web.application(urls, globals())

db = web.database(dbn='sqlite', db='branchbuilder.sqlite3')

class Index:

    def GET(self):

        i = web.input()
        if hasattr(i, 'pageLimit') and int(i.pageLimit) > 0:
            pageLimit = int(i.pageLimit)
        else:
            pageLimit = appconfig.per_page

        if hasattr(i, 'pageNum') and i.pageNum != ""  and int(i.pageNum) > 0:
            pageNum = int(i.pageNum)
        else:
            pageNum = 1

        branchBuilder = BranchBuilder(db)
        indexPage = branchBuilder.getIndexPage(pageNum, pageLimit)

        return render.index(indexPage["fix_builds"], appconfig.site_url, pageNum,
                            indexPage["total_page"], versionconfig.branchbuilder)

class SearchBuild:

    def GET(self):
        i = web.input()
        web.header('Content-type', 'application/json')

        branchBuilder = BranchBuilder(db)

        if not hasattr(i, "pageNum"):
            pageNum = 1
        else:
            pageNum = i.pageNum

        if hasattr(i, "q"):
            builds = branchBuilder.searchBuilds(**dict(i))
        else:
            return "[]"


        return json.JSONEncoder().encode({"builds": list(builds["builds"]), "builds_count": builds["builds_count"]})


class Add:

    def POST(self):
        i = web.input(styleguide_repo="", styleguide_branch="")

    # TODO
    # check duplicate
    # if found duplicate then build

        isDuplicate = False
        if isDuplicate:
            pass
        else:

    # else add a new build

            if hasattr(i, 'upgrade_package'):
                upgrade_package = i.upgrade_package
            else:
                upgrade_package = '0'

            if hasattr(i, 'latin'):
                latin = i.latin
            else:
                latin = '0'

            if hasattr(i, 'demo_data'):
                demo_data = i.demo_data
            else:
                demo_data = '1'

            if hasattr(i, 'expired_tag'):
                expired_tag = i.expired_tag
            else:
                expired_tag = '1'

            if hasattr(i, 'package_list'):
                package_list = i.package_list
            else:
                package_list = 'ent,pro'

            task_id  = uuid.uuid4()
            data = {
                'task_id': str(task_id),
                'repos': i.repos,
                'branch': i.branch,
                'version': i.version,
                'author': i.author,
                'styleguide_repo': i.styleguide_repo,
                'styleguide_branch': i.styleguide_branch,
                'sidecar_repo': i.sidecar_repo,
                'sidecar_branch': i.sidecar_branch,
                'build_number': '',
                'last_build_date': '',
                'start_time': '',
                'status': 'Available',
                'deploy_status': 'Unknown',
                'package_list': package_list,
                'upgrade_package': upgrade_package,
                'latin': latin,
                'demo_data': demo_data,
                'expired_tag': expired_tag
                }
            t = db.transaction()
            try:
                n = db.insert(
                    'builds',
                    **data
                    )
            except:
                t.rollback()
                raise
            else:
                t.commit()


            data["branch"] = BuildUtil().get_branch_name(data["branch"])
            logging.info("[Add Action:]" + json.dumps(data))
            web.header('Content-type', 'application/json')

            return json.dumps(data)


class Remove:

    def GET(self):
        i = web.input()

        for m in db.select('builds', where='task_id ="' + i.task_id + '"'):
            logging.info("[Delete Action:]" + json.dumps(m))

        t = db.transaction()
        try:
            n = db.delete('builds', where='task_id ="' + i.task_id + '"')
        except:
            t.rollback()
            raise
        else:
            t.commit()


class RunBuild:

    def run(self, task_id):

    # i = web.input()

        i = {'task_id': task_id}
        selectedBuilds = db.select('builds', where='task_id="'
                                   + str(i['task_id']) + '"')

        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if selectedBuilds:
            db.update('builds', where='task_id="' + str(i['task_id']) + '"',
                      last_build_date=date_now)

        taskBuilder = TaskBuilder('http://localhost:8080')

        for build in selectedBuilds:
            taskBuilder.add_build(
                repos=build.repos,
                branch=build.branch,
                version=build.version,
                author=build.author,
                styleguide_repo=build.styleguide_repo,
                styleguide_branch=build.styleguide_branch,
                sidecar_repo=build.sidecar_repo,
                sidecar_branch=build.sidecar_branch,
                package_list=build.package_list,
                upgrade_package=build.upgrade_package,
                latin=build.latin,
                demo_data=build.demo_data,
                )


    # raise web.seeother('/')

class Build:

    def GET(self):

        i = web.input()
        selected_fileds = ' \
            task_id, repos, branch, version, author, package_list, \
            upgrade_package, styleguide_repo, styleguide_branch, sidecar_repo, \
            sidecar_branch, demo_data, latin'
        selectedBuilds = db.select('builds', where='task_id="'
                                   + str(i.task_id) + '"', what=selected_fileds)[0]

        if selectedBuilds:
            builds_status = db.query('select * from builds_status')
            priority = 1;

            if builds_status:
                existing_build = db.query('select task_id from builds_status where task_id="' + i.task_id + '"')
                if len(list(existing_build)) == 0:
                    max_priority_records = \
                        db.query('select max(priority) as priority from builds_status')
                    priority = max_priority_records[0].priority + 1

            kue_job_id,kue_job_status = None, None
            job_url = appconfig.kue_server + '/job'
            playload = {
                    'type': 'sugarbuild',
                    'data': dict(selectedBuilds),
                    'options': {
                        'priority': priority,
                        'attempts': 2
                        }
                    }
            headers = {'content-type': 'application/json'}
            job_status = 'InQueue'

            try:
                r = requests.post(job_url, data = json.dumps(playload), headers = headers)
                kue_job_id = json.loads(r.text)['id']
            except Exception as e:
                web.debug('Failed to create kue job')

            try:
                r = requests.get(job_url + '/' + str(kue_job_id))
                kue_job_status = json.loads(r.text)['state']
            except Exception as e:
                web.debug('Failed to retrieve the job ' + str(kue_job_id))

            if kue_job_status == 'active':
                job_status = 'Running'

            t = db.transaction()
            try:
                n = db.insert('builds_status', 
                        task_id=str(i.task_id),
                        priority=priority, status=job_status,
                        kue_job_id=kue_job_id)
            except:
                t.rollback()
                raise
            else:
                t.commit()

            statusString = \
                json.JSONEncoder().encode({'task_id': i.task_id,
                    'status': job_status})

            web.header('Content-type', 'application/json')

            return statusString


class UpdateBuild:

    def POST(self):
        i = web.input(all_language_packs='0')

        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Before update

        for m in db.select('builds', where='task_id ="' + i.task_id + '"'):
            logging.info("[Before Update Action:]" + json.dumps(m))

        selectedBuilds = db.select('builds', where='task_id="'
                                   + i.task_id + '"')

        buildUtil = BuildUtil()
        i = buildUtil.sanitize_input(i)
        styleguide_branch = \
            buildUtil.determine_styleguide_branch(i.styleguide_repo,
                i.styleguide_branch, i.version)

        build_string = json.dumps([])
        if selectedBuilds:
            t = db.transaction()
            try:
                db.update(
                    'builds',
                    where='task_id="' + i.task_id + '"',
                    repos=i.repos,
                    branch=i.branch,
                    version=i.version,
                    author=i.author,
                    styleguide_repo=i.styleguide_repo,
                    styleguide_branch=styleguide_branch,
                    sidecar_repo=i.sidecar_repo,
                    sidecar_branch=i.sidecar_branch,
                    package_list=i.package_list,
                    upgrade_package=i.upgrade_package,
                    latin=i.latin,
                    demo_data=i.demo_data,
                    expired_tag=i.expired_tag
                    )
            except:
                t.rollback()
                raise
            else:
                t.commit()

          # After update

            for k in db.select('builds', where='task_id ="' + i.task_id + '"'):
                build_string = json.dumps(dict(k))
                logging.info("[After Update Action:]" + json.dumps(k))

        # End logger
        web.header('Content-type', 'application/json')
        return build_string


class GetBuild:

    def GET(self):
        i = web.input()
        buildString = ''
        selectedBuilds = db.select('builds', where='task_id="'
                                   + str(i.task_id) + '"')

        if selectedBuilds:
            for x in selectedBuilds:
                buildString = json.JSONEncoder().encode({
                    'task_id': i.task_id,
                    'repos': x.repos,
                    'branch': x.branch,
                    'version': x.version,
                    'author': x.author,
                    'latin': x.latin,
                    'demo_data': x.demo_data,
                    'styleguide_repo': x.styleguide_repo,
                    'styleguide_branch': x.styleguide_branch,
                    'sidecar_repo': x.sidecar_repo,
                    'sidecar_branch': x.sidecar_branch,
                    'package_list': x.package_list,
                    'upgrade_package': x.upgrade_package,
                    'expired_tag': x.expired_tag
                    })
            web.header('Content-type', 'application/json')
            return buildString


class StopBuild:

    def GET(self):
        i = web.input()
        jobInQueue = \
            db.query('select * from builds_status where task_id="'
                     + i.task_id + '"')
        job_inqueue_list = list(jobInQueue)
        if len(job_inqueue_list) > 0:
            kue_job_id = job_inqueue_list[0]["kue_job_id"]
            db.delete('builds_status', where='task_id="' + i.task_id + '"')
            db.update('builds', where='task_id="' + i.task_id + '"', deploy_status='Canceled', status='Canceled')

            try:
                job_url = appconfig.kue_server + '/job'
                r = requests.delete(job_url + '/' + str(kue_job_id))
                kue_job_status = json.loads(r.text)['state']
            except Exception as e:
                web.debug('Failed to remove the job ' + str(kue_job_id))

        web.seeother('/')

class BuildStatus:

    def POST(self):
        i = web.input()
        job_status = 'Available'
        deploy_status = 'Unknown'
        final_status = 'Available'

        if i.status :
            if i.status == 'complete' :
                job_status = 'Available'
                final_status = 'Available'
                t = db.transaction()
                try:
                    n = db.delete(
                        'builds_status',
                        where='task_id="' + i.task_id + '"'
                        )
                except:
                    t.rollback()
                    raise
                else:
                    t.commit()
            elif i.status == 'failed' :
                job_status = 'Failed'
                final_status = 'Failed'
                t = db.transaction()
                try:
                    n = db.delete(
                        'builds_status',
                        where='task_id="' + i.task_id + '"'
                        )
                except:
                    t.rollback()
                    raise
                else:
                    t.commit()
            elif i.status == 'progress' :
                if i.progress and int(i.progress) < 100:
                    job_status = 'Running'
                    t = db.transaction()
                    try:
                        n = db.update(
                            'builds_status',
                            where='task_id="' + i.task_id + '"',
                            status=job_status
                            )
                    except:
                        t.rollback()
                        raise
                    else:
                        t.commit()
                else:
                    job_status = 'Available'

            t = db.transaction()
            try:
                if i.status != 'progress':
                    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if i.deploy_status:
                        deploy_status = i.deploy_status.lower().title()
                    n = db.update(
                        'builds',
                        where='task_id="' + i.task_id + '"',
                        status=final_status,
                        deploy_status=deploy_status,
                        last_build_date=date_now
                        )
            except:
                t.rollback()
                raise
            else:
                t.commit()
        else:
            pass

class BuildCron:

    def run_cron(self):
        return db.select('builds_status', what='task_id, status, priority, kue_job_id')

    def GET(self):
        job_list = self.run_cron()
        web.header('Content-type', 'application/json')

        return json.JSONEncoder().encode(list(job_list))

class SendMailToAdmin:

    def POST(self):
        """
        i = web.input()
        web.sendmail(i.from_address, 'oyang@sugarcrm.com',
                     'BranchBuilder - ' + i.subject, i.message)
        """
        pass

class MappedVersion:
	def GET(self):
		i = web.input(version="")
		web.header('Content-type', 'application/json')
		branchbuilder = versionconfig.branchbuilder
		
		if i.version in branchbuilder.keys():       
			return json.JSONEncoder().encode(branchbuilder[i.version])
		else:
			return '{}'

class Logger:

    def GET(self):
        web.header('Content-type', 'text/plain')
        f = open('logger', 'r')
        return f.read()


if __name__ == '__main__':
    app.run()
