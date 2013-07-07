import os
import sys
import subprocess
import shutil
import time
import datetime
import glob
import web
import logging

from taskutil import TaskUtil


class BuildTask(object):
    def __init__(self):
        pass

    def execute(self):
        pass

class PruneBuildTask(BuildTask):

    def __init__(self, build_dirs, builder_db_path):
        super(PruneBuildTask, self).__init__()
        self.build_dirs = build_dirs
        self.builder_db_path = builder_db_path
        self.db = None

    def execute(self):
        self.prune_builds(self.build_dirs)

    def prune_builds(self, build_dirs):
        filter_build_dirs = self.get_prune_list(build_dirs, self.get_exempt_list())
        
        for build_dir in filter_build_dirs:
            print "Info: build dir is {}".format(build_dir)
            if self.available_to_prune(build_dir):
                sugar_build = self.get_build_info(build_dir)
                self.prune_sugar_build(sugar_build)
        
        self.prune_builder_db()

                
    def get_exempt_list(self):
        exempt_list = []
        db = self.get_builder_db()
        if db != None:
            exempt_list_sql = """
            select * from  builds
            where expire_flag = 1;
            """
            
            for task in db.query(exempt_list_sql):
                for flavor in task.package_list:
                    instance_name = flavor.lower() + TaskUtil().generate_user_name(task.author) + task.branch
                    exempt_list.append(instance_name)
                
        return exempt_list
    
    def get_prune_list(self, build_dirs, filter_list):
        return [build for build in build_dirs if build not in filter_list]
    
    def get_build_info(self, build_dir):
        sugar_build = {"build_dir": build_dir}
        old_pwd = os.getcwd()
        os.chdir(build_dir)

        get_db_host_cmd = [ 
                'php',
                '-r',
                'require_once("config.php");echo $sugar_config["dbconfig"]["db_host_name"];'
            ]
        get_db_name_cmd = [ 
                'php',
                '-r',
                'require_once("config.php");echo $sugar_config["dbconfig"]["db_name"];'
            ]
        get_db_user_cmd = [
                'php',
                '-r',
                'require("config.php");echo $sugar_config["dbconfig"]["db_user_name"];'
             ]
        get_db_passwd_cmd = [
                'php',
                '-r',
                'require("config.php");echo $sugar_config["dbconfig"]["db_password"];'
             ]
        try:
            sugar_build["sugar_build_db_host"] = subprocess.check_output(get_db_host_cmd)
            sugar_build["sugar_build_db_name"] = subprocess.check_output(get_db_name_cmd)
            sugar_build["sugar_build_db_user"] = subprocess.check_output(get_db_user_cmd)
            sugar_build["sugar_build_db_passwd"] = subprocess.check_output(get_db_passwd_cmd)
            sugar_build["build_dir"] = build_dir
        except subprocess.CalledProcessError:
            print "Fatal: can not get sugar db info"
            print sugar_build
            return False
        
        os.chdir(old_pwd)
        return sugar_build

    def get_elapsed_time(self, build_dir):
        created_time = os.path.getctime(build_dir + "/install.log")
        current_time = time.time()

        return current_time - created_time

    def elapse_specific_time(self, **args):
        duration_delta = datetime.timedelta(**args)

        return duration_delta.total_seconds()

    def check_build_eplapsed_time(self, build_dir, **time):
        elapsed_time = self.get_elapsed_time(build_dir)
        if len(time) == 0:
            time = {"weeks": 2}

        if elapsed_time >= self.elapse_specific_time(**time):
            return True
        else:
            return False

    def available_to_prune(self, build_dir):
        if self.is_sugar_build(build_dir):
            if self.check_build_eplapsed_time(build_dir, hours=1):
                return True
            
        return False

    def get_builder_db(self):
        if self.db == None:
            try:
                self.db = web.database(dbn = "sqlite", db = self.builder_db_path)
            except Exception:
                print "Fatal: can not open {}".format(self.builder_db_path)
                return None

        return None

    def is_sugar_build(self, build_dir):
        if os.path.exists(build_dir):
            build_dir = os.path.realpath(build_dir)
            sugar_version = build_dir + "/sugar_version.php"
            sugar_bean = build_dir + "/data/SugarBean.php"

            if os.path.exists(sugar_version) and os.path.exists(sugar_bean):
                return True

        return False

    def prune_sugar_build(self, sugar_build):
        self.prune_build_dir(sugar_build)
        self.prune_build_db(sugar_build)

    def prune_builder_db(self):
        db = self.get_builder_db()
        if db != None:
            db_prune_list_sql = """
            delete from builds
            where expire_flag = 0 and strftime('%s', 'now', 'localtime') - strftime('%s', last_build_date, 'localtime') >= 2*7*24*60*60;
            """
            db.query(db_prune_list_sql)

    def prune_build_dir(self, sugar_build):
        shutil.rmtree(sugar_build["build_dir"]) 

    def prune_build_db(self, sugar_build):
        db_clean_cmd = [
                "mysqladmin",
                "-f",
                "-h" + sugar_build["sugar_build_db_host"],
                "-u" + sugar_build["sugar_build_db_user"],
                "-p" + sugar_build["sugar_build_db_passwd"],
                "drop",
                sugar_build["sugar_build_db_name"]
                ]
        try:
            subprocess.check_output(db_clean_cmd, stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "database doesn't exist" in e.output:
                print "Info: database {} was already pruned".format(sugar_build["sugar_build_db_name"]) 
                return True
            else:
                print "Error: prune sugar db failed {}".format(sugar_build["sugar_build_db_name"])
                return False

def main():
    logging.basicConfig(filename="prunebuildtask.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    BUILD_DIRS_PARENT = "/var/www"
    old_pwd = os.getcwd()
    os.chdir(BUILD_DIRS_PARENT)
    BUILDER_DB_PATH = "/var/www/branchbuilder.sqlite3"

    pruneBuildTask = PruneBuildTask(glob.glob("*"), BUILDER_DB_PATH)
    pruneBuildTask.execute()
    os.chdir(old_pwd)

if __name__ == "__main__":
    main()
