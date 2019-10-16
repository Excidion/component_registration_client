import pymysql
from time import sleep
import os
from utils import pickle_object, unpickle_object


class ConnectionManager:
    def __init__(self, config):
        self.config = config
        self.storage = "login.p"
        if os.path.exists(self.storage):
            stored = unpickle_object(self.storage)
            self.set_credentials(stored["user"], stored["passwd"])
        self.open_jobs = "jobs.p"

    def set_credentials(self, user, password, store=False):
        self.config["user"] = user
        self.config["passwd"] = password
        if store:
            pickle_object({"user": user, "passwd": password}, self.storage)


    def check_part_existence(self, id, allow_offline=False):
        if not self.check_online_status():
            return allow_offline # allow offline editing

        query = f"SQL asking for amount of entries for {id}"
        entries = self.execute_query(query)
        return len(entries) > 0

    def check_online_status(self):
        try:
            pymysql.connect(**self.config).close()
        except UnicodeError:
            print("Error in MySQL configuration.")
        except pymysql.err.OperationalError as e:
            print(e)
        else:
            self.execute_jobs()
            return True
        return False

    def execute_jobs(self, append_query=None):
        jobs = self.get_open_jobs()
        if not append_query == None:
            jobs.append(query)
        for i, job in enumerate(jobs):
            try:
                self.execute_query(job)
            except Exception as e:
                print(e)
                continue
            else:
                del jobs[i]
        pickle_object(jobs, self.open_jobs)

    def get_open_jobs(self):
        try:
            return unpickle_object(self.open_jobs)
        except FileNotFoundError:
            return []

    def execute_query(self, query):
        db = pymysql.connect(**self.config)
        cur = db.cursor()
        cur.execute(query)
        result = cur.fetchall()
        db.close()
        return result


    def wait_for_changes(self):
        query = "magic query to ask for last update" # TODO
        db = pymysql.connect(**self.config)
        cur = db.cursor()
        while not sleep(5):
            cur.execute(query)
            last_entry = cur.fetchall()
            if last_entry == my_last_entry:
                return
