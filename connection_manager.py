import pymysql
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
from time import sleep
import os
from utils import pickle_object, unpickle_object, encrypt_string, decrypt_string, generate_event_id


class ConnectionManager:
    def __init__(self, config):
        self.open_jobs = ".jobs.p"
        self.config = config
        self.storage = ".login.p"
        if os.path.exists(self.storage):
            stored = unpickle_object(self.storage)
            self.set_credentials(
                decrypt_string(stored["user"]),
                decrypt_string(stored["passwd"]),
            )


    def set_credentials(self, user, password, store=False):
        self.config["user"] = user
        self.config["passwd"] = password
        if store:
            pickle_object(
                {
                    "user": encrypt_string(user),
                    "passwd": encrypt_string(password),
                },
            self.storage,
            )

    def get_unique(self, column):
        data = self.get_table("components")
        return list(data[column].unique())

    def get_part_data(self, id):
        data = self.get_table("components")
        data = data[data["id"] == id]
        data.sort_values("time", inplace=True, ascending=False)
        return data.iloc[0].squeeze()

    def get_table(self, table_name):
        user = self.config["user"]
        pwd = self.config["passwd"]
        host = self.config["host"]
        db = self.config["database"]
        with create_engine(f"mysql+pymysql://{user}:{pwd}@{host}/{db}").connect() as con:
            return pd.read_sql(table_name, con=con)


    def submit_part(self, data):
        self.append_table("components", data)

    def append_table(self, table_name, data):
        data["user"] = self.config["user"]
        data["event_id"] = data["id"].apply(generate_event_id)
        data["event_time"] = datetime.utcnow()
        user = self.config["user"]
        pwd = self.config["passwd"]
        host = self.config["host"]
        db = self.config["database"]
        with create_engine(f"mysql+pymysql://{user}:{pwd}@{host}/{db}").connect() as con:
            data.to_sql(table_name, con=con, if_exists="append", index=False)


    def check_part_existence(self, id, allow_offline=False):
        if not self.check_online_status():
            return allow_offline
        data = self.get_table("components")
        return id in data["id"].unique()

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
        pickle_object([encrypt_string(j) for j in jobs], self.open_jobs)

    def get_open_jobs(self):
        try:
            return [decrypt_string(j) for j in unpickle_object(self.open_jobs)]
        except FileNotFoundError:
            return []

    def execute_query(self, query):
        with pymysql.connect(**self.config) as con:
            cur = con.cursor()
            cur.execute(query)
            result = cur.fetchall()
        return result
