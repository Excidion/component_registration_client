from uuid import uuid4
import hashlib
from datetime import datetime
from uuid import getnode as get_mac_adress
import pickle


def generate_part_id():
    return str(uuid4()).replace("-", "")


def generate_event_id(part_id):
    timestamp = str(datetime.utcnow())
    mac_adress = get_mac_adress()
    salt = f"{mac_adress}@{timestamp}"
    return hash_string(part_id, salt=salt)


def hash_string(string, salt=None):
    if isinstance(salt, str):
        string += salt # TODO proper salting ?
    return hashlib.sha1(string.encode()).hexdigest()


def pickle_object(object, filepath):
    with open(filepath, "wb") as file:
        pickle.dump(object, file)

def unpickle_object(filepath):
    with open(filepath, "rb") as file:
        return pickle.load(file)
