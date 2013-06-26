#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import web
from jenkins import Jenkins

import json
import urllib2
import re
from datetime import datetime

from buildutil import *
import BuildConfig
import ODDeploy
import CIDeploy
import Nomad
import appconfig
from models.branchbuilder import BranchBuilder

render = web.template.render('template/', base='layout')
urls = (
    '/', 'Index',
    '/add', 'Add',
    '/build', 'Build',
    '/getbuild', 'GetBuild',
    '/stopbuild', 'StopBuild',
    '/searchbuild', 'SearchBuild',
    '/updatebuild', 'UpdateBuild',
    '/remove', 'Remove',
    '/sendmail', 'SendMailToAdmin',
    '/cron', 'BuildCron',
    '/fullview', 'FullView',
    '/logger', 'Logger',
    '/buildconfig', BuildConfig.app_BuildConfig,
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
                            indexPage["total_page"])

    def update_status(self):
        builds_status = db.select('builds_status')

        for build_status in builds_status:
            db.update('builds', where='task_id="'
                      + str(build_status.task_id) + '"',
                      status=build_status.status)

    def get_job_name(self, string):
        buildUtil = BuildUtil()
        return buildUtil.get_job_name(repos=string)


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
            builds = branchBuilder.searchBuilds(q = i.q, pageNum = int(pageNum))
        else:
            return "[]"


        return json.JSONEncoder().encode({"builds": builds["builds"], "builds_count": builds["builds_count"]})


class Add:

    def POST(self):
        i = web.input()

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
                upgrade_package = 0

            if hasattr(i, 'latin'):
                latin = i.latin
            else:
                latin = 0

            if hasattr(i, 'demo_data'):
                demo_data = i.demo_data
            else:
                demo_data = 1

            buildUtil = BuildUtil()
            i = buildUtil.sanitize_input(i)
            styleguide_branch = \
                buildUtil.determine_styleguide_branch(i.styleguide_repo,
                    i.styleguide_branch, i.version)
            task_id  = int(db.query("select max(rowid), task_id from builds")[0]["task_id"]) + 1
            n = db.insert(
                'builds',
                task_id = str(task_id),
                repos=i.repos,
                branch=i.branch,
                version=i.version,
                author=i.author,
                styleguide_repo=i.styleguide_repo,
                styleguide_branch=styleguide_branch,
                sidecar_repo=i.sidecar_repo,
                sidecar_branch=i.sidecar_branch,
                build_number=1000,
                last_build_date='',
                start_time='',
                status='Available',
                package_list='ent',
                upgrade_package=upgrade_package,
                latin=latin,
                demo_data=demo_data,
                )

            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f = open('logger', 'a')
            f.write(date_now + ' [Add Action:],' + i.repos + ','
                    + i.branch + ',' + i.version + ',' + i.author + ','
                    + i.styleguide_repo + ',' + i.styleguide_branch
                    + ',' + i.sidecar_repo + ',' + i.sidecar_branch
                    + ', ent, Available' + str(upgrade_package) + '\n')
            f.close()
            raise web.seeother('/')


class Remove:

    def GET(self):
        i = web.input()
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        f = open('logger', 'a')
        for m in db.select('builds', where='task_id ="' + i.task_id + '"'):
            f.write(date_now + ' [Delete Action:]' + str(m.task_id)
                    + ',' + m.repos + ',' + m.branch + ',' + m.version
                    + ',' + m.author + ',' + m.styleguide_repo + ','
                    + m.styleguide_branch + ',' + m.sidecar_repo + ','
                    + m.sidecar_branch + ',' + m.package_list + '\n')
        f.close()

        n = db.delete('builds', where='task_id ="' + i.task_id + '"')


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
        selectedBuilds = db.select('builds', where='task_id="'
                                   + str(i.task_id) + '"', what='task_id')

        if selectedBuilds:
            builds_status = db.select('builds_status')

            if builds_status:
                max_priority_records = \
                    db.query('select max(priority) as priority from builds_status'
                             )
                new_max_priority = max_priority_records[0].priority + 1

                db.insert('builds_status', task_id=int(i.task_id),
                          priority=new_max_priority, status='InQueue')
                statusString = \
                    json.JSONEncoder().encode({'task_id': i.task_id,
                        'status': 'InQueue'})
            else:
                db.insert('builds_status', task_id=int(i.task_id),
                          status='Running', priority=1)
                RunBuild().run(i.task_id)
                statusString = \
                    json.JSONEncoder().encode({'task_id': i.task_id,
                        'status': 'Running'})

            return statusString


class UpdateBuild:

    def POST(self):
        i = web.input(all_language_packs='0')

        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Before update

        f = open('logger', 'a')
        for m in db.select('builds', where='task_id ="' + i.task_id + '"'):
            f.write(date_now + ' [Before Update Action:]'
                    + str(m.task_id) + ',' + m.repos + ',' + m.branch
                    + ',' + m.version + ',' + m.author + ','
                    + m.styleguide_repo + ',' + m.styleguide_branch
                    + ',' + m.sidecar_repo + ',' + m.sidecar_branch
                    + ',' + m.package_list + ',' + str(m.latin) + ','
                    + str(m.demo_data) + ',' + '\n')

        selectedBuilds = db.select('builds', where='task_id="'
                                   + i.task_id + '"')

        buildUtil = BuildUtil()
        i = buildUtil.sanitize_input(i)
        styleguide_branch = \
            buildUtil.determine_styleguide_branch(i.styleguide_repo,
                i.styleguide_branch, i.version)

        build_string = json.dumps([])
        if selectedBuilds:
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
                )

          # After update

            for k in db.select('builds', where='task_id ="' + i.task_id + '"'):
                build_string = json.dumps(dict(k))
                f.write(date_now + ' [After Update Action:]'
                        + str(k.task_id) + ',' + k.repos + ','
                        + k.branch + ',' + k.version + ',' + k.author
                        + ',' + k.styleguide_repo + ','
                        + k.styleguide_branch + ',' + k.sidecar_repo
                        + ',' + k.sidecar_branch + ',' + k.package_list
                        + ',' + str(k.latin) + ',' + str(k.demo_data)
                        + '\n')

        f.close()

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
                    })
            web.header('Content-type', 'application/json')
            return buildString


class StopBuild:

    def GET(self):
        i = web.input()
        jobInQueue = \
            db.query('select * from builds_status where task_id="'
                     + i.task_id + '" and status="InQueue"')
        if len(jobInQueue.list()) > 0:
            db.delete('builds_status', where='task_id="' + i.task_id + '"')
            web.seeother('/')

        selectedBuilds = db.query('select repos from builds where task_id="' + i.task_id + '"')
        for x in selectedBuilds:
            jobName = BuildUtil().get_job_name(repos=x.repos)
            TaskBuilder(appconfig.jenkins_url).stop_jenkins_jobs(jobName)

        web.seeother('/')


class BuildCron:

    def __init__(self):
        self.taskBuilder = TaskBuilder(appconfig.jenkins_url)

    def check_queue(self):

    # Check queue jobs

        j = self.taskBuilder.j

        return j.get_queue_info()

    def is_building_job(self, jobName):
        if str(jobName) in self.get_building_job():
            return True
        else:
            return False

    def get_building_job(self):

    # Check building job

        j = self.taskBuilder.j
        job_list = j.get_jobs()
        job_queue_list = j.get_queue_info()
        running_job = []

        for job in job_list:
            if re.search('anime', job['color']) and re.match('^Build_',
                    job['name']):
                running_job.append(job['name'])

        for queue_item in job_queue_list:
            if re.match('^Build_', queue_item['task']['name']):
                running_job.append(queue_item['task']['name'])

        return running_job

    def get_lowest_build(self):
        min_builds = \
            db.query('select task_id, status, priority \
           from builds_status \
           where priority=(select min(b.priority) from builds_status as b)'
                     )
        if min_builds:
            for min_build in min_builds:
                return {'task_id': min_build.task_id,
                        'status': min_build.status,
                        'priority': min_build.priority}

    def update_task_status_as_lastBuild(self, task_id, jobName):
        j = self.taskBuilder
        job_status = j.get_build_status(jobName)

        if job_status == False or job_status == 'Succcess' or job_status == 'Running':
            job_status = 'Available'

        db.update('builds', where='task_id="' + str(task_id) + '"',
                  status=job_status)

    def run_cron(self):
        lowest_build = self.get_lowest_build()
        job_list = []

        if lowest_build:
            if lowest_build['status'] == 'Running':
                selectRepos = db.select('builds', where='task_id="'
                        + str(lowest_build['task_id']) + '"', what='repos')
                buildUtil = BuildUtil()
                jobName = ''
                for m in selectRepos:
                    jobName = buildUtil.get_job_name(repos=m['repos'])

                if self.is_building_job(jobName):
                    pass
                else:
                    # update build_status and remove the running flag
                    self.update_task_status_as_lastBuild(str(lowest_build['task_id'
                            ]), jobName)
                    db.delete('builds_status', where='task_id="'
                              + str(lowest_build['task_id']) + '"')
            elif lowest_build['status'] == 'InQueue':
                # Assume Jenkins is avaliable for building
                RunBuild().run(lowest_build['task_id'])
                db.update('builds_status', where='task_id="'
                          + str(lowest_build['task_id']) + '"',
                          status='Running')
            else:
                pass
        else:
            # print 'false from lowest build'
            pass

        for x in db.select('builds_status', what='task_id, status'):
            job_list.append(x)

        return job_list

    def GET(self):
        job_list = []
        new_builds_status = self.run_cron()
        web.header('Content-type', 'application/json')
        if new_builds_status:
            for build_status in new_builds_status:
                job_list.append({'task_id': build_status.task_id,
                                'status': build_status.status})

        return json.JSONEncoder().encode(job_list)


class FullView:

    def POST(self):
        i = web.input()
        builds = db.select('builds', where='task_id =' + i.task_id)

        return render.view(builds)

    def GET(self):
        i = web.input()
        builds = db.select('builds', where='task_id =' + i.task_id)

        return render.view(builds)


class Fixing:

    def GET(self):
        i = web.input()

        return render.fixing(appconfig.site_url)


class SendMailToAdmin:

    def POST(self):
        i = web.input()
        web.sendmail(i.from_address, 'oyang@sugarcrm.com',
                     'BranchBuilder - ' + i.subject, i.message)


class Logger:

    def GET(self):
        web.header('Content-type', 'text/plain')
        f = open('logger', 'r')
        return f.read()


if __name__ == '__main__':
    app.run()
