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

    def set_credentials(self, user, password, store=False):
        self.config["user"] = user
        self.config["passwd"] = password
        if store:
            pickle_object({"user": user, "passwd": password}, self.storage)


    def execute_query(self, query):
        db = pymysql.connect(**self.config)
        cur = db.cursor()
        cur.execute(query)
        result = cur.fetchall()
        db.close()
        return result


    def check_online_status(self):
        try:
            pymysql.connect(**self.config).close()
        except Exception as e:
            print(e)
            return False
        else:
            return True


    def wait_for_changes(self):
        query = "magic query" # TODO query to return if anything changed
        db = pymysql.connect(**self.config)
        cur = db.cursor()
        while not sleep(1):
            try:
                cur.execute(query)
                new_entries = cur.fetchall()
            except Exception as e:
                print(e)
                sleep(1)
            else:
                if new_entries:
                    db.close()
                    return
