import os
import subprocess
import shutil
import time
import datetime
import glob
import web
import logging

from taskutil import BuildTask, TaskUtil


class PruneBuildTask(BuildTask):
    """
    This prune build task will prune all the sugar build in specific directory
    """

    def __init__(self, build_dirs, builder_db_path, build_installer_parent):
        super(PruneBuildTask, self).__init__()
        self.build_dirs = build_dirs
        self.builder_db_path = builder_db_path
        self.build_installer_parent = build_installer_parent
        self.db = None

    
    def execute(self):
        """
        main execute entry point
        """
        self.prune_builds(self.build_dirs)

    
    def prune_builds(self, build_dirs):
        """
        @build_dirs build dir list 
        @return None
        """
        filter_build_dirs = self.get_prune_list(build_dirs, self.get_exempt_list())
        
        for build_dir in filter_build_dirs:
            print "Info: build dir is {}".format(build_dir)
            if self.available_to_prune(build_dir):
                sugar_build = self.get_build_info(build_dir)
                self.prune_sugar_build(sugar_build)
        
        self.prune_builder_db()
                
    
    def get_exempt_list(self):
        """
        @return exempt list
        """
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
        else:
            raise Exception("Can not get db connection!")
                
        return exempt_list
    
    
    def get_prune_list(self, build_dirs, filter_list):
        """
        @param build_dirs all the build dris
        @param filter_list exempt list
        @return build dir list which will be pruned
        """
        return [build for build in build_dirs if build not in filter_list]
    
    
    def get_build_info(self, build_dir):
        """
        @param build_dir for single build dir
        @return
        """
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
        get_sugar_flavor_cmd = [
                'php',
                '-r',
                'require("sugar_version.php");echo strtolower($sugar_flavor);'
             ]
        try:
            sugar_build["sugar_build_db_host"] = subprocess.check_output(get_db_host_cmd)
            sugar_build["sugar_build_db_name"] = subprocess.check_output(get_db_name_cmd)
            sugar_build["sugar_build_db_user"] = subprocess.check_output(get_db_user_cmd)
            sugar_build["sugar_build_db_passwd"] = subprocess.check_output(get_db_passwd_cmd)
            sugar_build["build_dir"] = build_dir
            sugar_build["sugar_build_flavor"] = subprocess.check_output(get_sugar_flavor_cmd)
            sugar_build["sugar_installer_dir"] = os.path.realpath(self.build_installer_parent) + "/" + build_dir[len(sugar_build["sugar_build_flavor"]):]
        except subprocess.CalledProcessError:
            print "Fatal: can not get sugar db info"
            print sugar_build
            return False
        
        os.chdir(old_pwd)
        return sugar_build

    
    def get_elapsed_time(self, build_dir):
        """
        @param build_dir signle sguar build dir
        @return get elapsed time as seconds
        """
        created_time = os.path.getctime(build_dir + "/install.log")
        current_time = time.time()

        return current_time - created_time

    
    def elapse_specific_time(self, **args):
        """
        @param args time format
        @return total seconds in duration
        """
        duration_delta = datetime.timedelta(**args)

        return duration_delta.total_seconds()

    
    def check_build_eplapsed_time(self, build_dir, **time_duration):
        """
        @param build_dir
        @param time_duration
        @return get the result to check whether build dir has elapsed given time
        """
        elapsed_time_duration = self.get_elapsed_time(build_dir)
        if len(time_duration) == 0:
            time_duration = {"weeks": 2}

        if elapsed_time_duration >= self.elapse_specific_time(**time_duration):
            return True
        else:
            return False

    
    def available_to_prune(self, build_dir):
        """
        @param build_dir
        @return get the status if current build should be pruned
        """
        if self.is_sugar_build(build_dir):
            if self.check_build_eplapsed_time(build_dir, hours=1):
                return True
            
        return False

    
    def get_builder_db(self):
        """
        @return branch builder DB
        """
        if self.db == None:
            try:
                self.db = web.database(dbn = "sqlite", db = self.builder_db_path)
            except Exception:
                print "Fatal: can not open {}".format(self.builder_db_path)
                return None

        return self.db

    
    def is_sugar_build(self, build_dir):
        """
        @param build_dir
        @return get the staus if current build is sugar build
        """
        if os.path.exists(build_dir):
            build_dir = os.path.realpath(build_dir)
            sugar_version = build_dir + "/sugar_version.php"
            sugar_bean = build_dir + "/data/SugarBean.php"

            if os.path.exists(sugar_version) and os.path.exists(sugar_bean):
                return True

        return False

    
    def prune_sugar_build(self, sugar_build):
        """
        @param sugar_build build object
        @return None
        """
        self.prune_build_dir(sugar_build)
        self.prune_build_db(sugar_build)
        self.prune_build_installer(sugar_build)
        self.prune_build_summary_page(sugar_build)

    def prune_build_summary_page(self, sugar_build):
        """
        @param sugar_build build object
        @return None
        """
        if os.path.exists(sugar_build["sugar_installer_dir"]) and sugar_build["sugar_installer_dir"] != self.build_installer_parent:
            build_summary_page = os.path.dirname(sugar_build["sugar_installer_dir"]) + "/build" + os.path.basename(sugar_build["sugar_installer_dir"]) + ".html"
            if os.path.exists(build_summary_page):
                shutil.rmtree(build_summary_page)
            else:
                print "Skipped: Can not find build_summary_page {}".format(build_summary_page)
        else:
            print "Can not find sugar build install dir {}".format(sugar_build["sugar_installer_dir"])

    def prune_build_installer(self, sugar_build):
        """
        @param sugar_build build object
        @return None
        """
        if os.path.exists(sugar_build["sugar_installer_dir"]) and sugar_build["sugar_installer_dir"] != self.build_installer_parent:
            shutil.rmtree(sugar_build["sugar_installer_dir"])
        else:
            print "Can not find sugar build install dir {}".format(sugar_build["sugar_installer_dir"])
    
    def prune_builder_db(self):
        """
        Prune branch builder DB
        @return None
        """
        db = self.get_builder_db()
        if db != None:
            time_duration = datetime.timedelta(weeks=2).total_seconds()
            db_prune_list_sql = """
            delete from builds
            where expire_flag = 0 and strftime('%s', 'now', 'localtime') - strftime('%s', last_build_date, 'localtime') >= {};
            """.format(time_duration)
            db.query(db_prune_list_sql)

    
    def prune_build_dir(self, sugar_build):
        """
        @param sugar_build build object
        @return None
        """
        shutil.rmtree(sugar_build["build_dir"]) 

    
    def prune_build_db(self, sugar_build):
        """
        Prune sugar build DB and assume DB type is MySQL
        @param sugar_build bulid object
        @return None
        """
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
        except subprocess.CalledProcessError as exception:
            if "database doesn't exist" in exception.output:
                print "Info: database {} was already pruned".format(sugar_build["sugar_build_db_name"]) 
                return True
            else:
                print "Error: prune sugar db failed {}".format(sugar_build["sugar_build_db_name"])
                return False

def main():
    logging.basicConfig(filename="prunebuildtask.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    build_dirs_parent = "/var/www"
    build_installer_parent = "/var/www/public/builds"
    old_pwd = os.getcwd()
    os.chdir(build_dirs_parent)
    builder_db_path = "/var/www/BranchBuilder/branchbuilder.sqlite3"

    prunebuildtask = PruneBuildTask(glob.glob("*"), builder_db_path, build_installer_parent)
    prunebuildtask.execute()
    os.chdir(old_pwd)

if __name__ == "__main__":
    main()
