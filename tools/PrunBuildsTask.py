import os
import subprocess
import shutil
import time
import datetime
import sys
import glob
import web
import logging

sys.path.append("..")
from buildutil import BuildUtil

def todo(f):
    def inner_m():
        print "! TODO method"

    return inner_m 

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

    def execute(self):
        self.prune_builds(self.build_dirs)

    def prune_builds(self, build_dirs):
        for build_dir in build_dirs:
            if self.available_to_prune(build_dir):
                sugar_build = self.get_build_info(build_dir)
                self.prune_sugar_build(sugar_build)

    def get_build_info(self, build_dir):
        sugar_build = {"build_dir": build_dir}
        old_pwd = os.getcwd(build_dir)
        os.chdir(build_dir)

        get_db_host_name_cmd = [ 
            'php',
            '-r ',
            'require("config.php");echo $sugar_config["dbconfig"]["db_host_name"];'
            ]
        get_db_name_cmd = [ 
            'php',
            '-r ',
            'require("config.php");echo $sugar_config["dbconfig"]["db_name"];'
            ]
        get_db_user_cmd = [
                'php',
                '-r',
                'require("config.php");echo $sugar_config["dbconfig"]["db_user_name"];'
             ]
        get_db_user_passwd_cmd = [
                'php',
                '-r',
                'require("config.php");echo $sugar_config["dbconfig"]["db_password"];'
             ]
        try:
            sugar_build_db_host = subprocess.check_output(get_db_host_name_cmd)
            sugar_build_db_name = subprocess.check_output(get_db_name_cmd)
            sugar_build_db_user = subprocess.check_output(get_db_user_cmd)
            sugar_build_db_user_passwd = subprocess.check_output(get_db_user_passwd_cmd)

            sugar_build["sugar_build_db_host"] = sugar_build_db_host
            sugar_build["sugar_build_db_name"] = sugar_build_db_name
            sugar_build["sugar_build_db_user"] = sugar_build_db_user
            sugar_build["sugar_build_db_user_passwd"] = sugar_build_db_user_passwd
        except subprocess.CalledProcessError:
            print "Fatal: can not get sugar db name"
            return False
        
        os.chdir(old_pwd)
        return sugar_build

    def get_elapsed_time(self, build_dir):
        created_time = os.path.getctime(build_dir)
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

    @todo
    def marked_as_prune(self, sugar_build):
        pass

    @todo
    def available_to_prune(self, build_dir):
        if self.is_sugar_build(build_dir):
            if check_build_eplapsed_time(build_dir, weeks=2):
                sugar_build = self.get_build_info(build_dir)
                if self.find_build_in_db(sugar_build):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_builder_db(self):
        if not self.db:
            try:
                db = web.database(dbn = "sqlite3", db = self.builder_db_path)
                self.db = db
            except Exception:
                print "Fatal: can not open " + self.builder_db_path
                return None
        else:
            return self.db

    @todo
    def find_build_in_db(self, sugar_build):
        if os.path.exists(sugar_build["build_dir"]):
            query_string = ""
            db = self.get_builder_db()
            results = db.query(query_string)
        else:
            return False

    def is_sugar_build(self, instance_dir):
        if os.path.exists(instance_dir):
            instance_dir = os.path.realpath(instance_dir)
            sugar_version = instance_dir + "/sugar_version.php"
            sugar_bean = instance_dir + "/data/SugarBean.php"

            if os.path.exists(sugar_version) and os.path.exists(sugar_bean):
                return True

        return False

    def prune_sugar_build(self, sugar_build):
        self.prune_builder_db(sugar_build)
        self.prune_build_dir(sugar_build)
        self.prune_build_db(sugar_build)


    @todo
    def prune_builder_db(self, sugar_build):
        pass

    def prune_build_dir(self, sugar_build):
        shutil.rmtree(sugar_build["build_dir"]) 

    def prune_build_db(self, sugar_build):
        db_clean_cmd = [
                "mysqladmin"
                "-f",
                "-hhoney-g",
                "-uroot",
                "-psugarcrm",
                "drop",
                sugar_build["sugar_build_db_name"]
                ]
        try:
            subprocess.check_call(db_clean_cmd)
        except subprocess.CalledProcessError:
            print "Error: prune sugar db failed"
            return False

def main():
    logging.basicConfig(filename="prunebuildtask.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    BUILD_DIRS_PARENT = "/var/www"
    old_pwd = os.getcwd()
    os.chdir(BUILD_DIRS_PARENT)
    BUILDER_DB_PATH = ""

    pruneBuildTask = PruneBuildTask(glob.glob("*"), BUILDER_DB_PATH)
    pruneBuildTask.execute()
    os.chdir(old_pwd)

if __name__ == "__main__":
    main()
