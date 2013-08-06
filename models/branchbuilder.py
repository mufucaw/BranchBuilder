from sqlite3 import OperationalError
import web
import appconfig
from  buildutil import *

class BranchBuilder:

    def __init__(self, db):
        self.db = db
        self.buildUtil = BuildUtil()

    def searchBuilds(self, **params):
        if "limit" not in params.keys():
            params["limit"] = 20

        if "pageNum" in params.keys():
            params["offset"] = (int(params["pageNum"])  - 1) * appconfig.per_page
        else:
            params["offset"] = 0

        default_sql = """ 
            select task_id, status, build_number, author, repos, version, branch, last_build_date 
            from builds_status_left_join_view 
            order by status desc, last_build_date desc
            limit {}
            offset {}
            """.format(params["limit"], params["offset"])
        default_count_sql = """ 
            select count(*) as builds_count
            from builds_status_left_join_view 
            order by status desc, last_build_date desc
            """
        query_sql = """
            select task_id, status, build_number, author, repos, version, branch, last_build_date 
            from builds_status_left_join_view 
            where task_id in 
            ( select task_id 
              from builds 
              where builds match '{}' ) 
            order by status desc, last_build_date desc 
            limit {} 
            offset {}
            """.format(params["q"], params["limit"], params["offset"])

        builds_count_sql = """
            select count(*) as builds_count
            from builds_status_left_join_view 
            where task_id in 
            ( select task_id 
              from builds 
              where builds match '{}' ) 
            """.format(params["q"])

        if params["q"] == "": 
            query_sql = default_sql 
            builds_count_sql = default_count_sql

        web.debug(query_sql)
        web.debug("offset is " +  str(params["offset"]))
        # Rebuild builds list
        try:
            builds_list = list(self.db.query(query_sql))
        except OperationalError as error:
            return {"builds": [], "builds_count": 0}

        for build_index in range(0, len(builds_list)):
           builds_list[build_index]['username'] = self.buildUtil.generate_user_name(builds_list[build_index]['author'])
           builds_list[build_index]["build_number"] = self.buildUtil.get_build_number(builds_list[build_index])

        return {"builds": builds_list, "builds_count": self.db.query(builds_count_sql)[0]["builds_count"]} 

    def getIndexPage(self, pageNum = 1, pageLimit = appconfig.per_page):
        offset = (pageNum - 1) * appconfig.per_page
        builds = \
        self.db.query("select * \
          from builds_status_left_join_view \
          order by status desc, last_build_date desc \
          limit " + str(pageLimit) + ' offset ' + str(offset))

        fix_builds = []
        for build in builds:
           build['username'] = self.buildUtil.generate_user_name(build['author'])
           build["build_number"] = self.buildUtil.get_build_number(build)
           fix_builds.append(build)

        total_records_count = self.db.query('select count(*) as count from builds')[0].count
        plus_page = 0
        if total_records_count % appconfig.per_page != 0:
            plus_page = 1

        total_page = total_records_count / appconfig.per_page + plus_page

        return {"fix_builds": fix_builds, "total_page": total_page}
