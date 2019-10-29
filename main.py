from configparser import ConfigParser
from user_interface import UserInterface
from connection_manager import ConnectionManager


def main():
    config = ConfigParser()
    config.read("config.ini")

    cm_config = {
        "host": config.get("SQL", "host_address"),
        "port": config.getint("SQL", "port"),
        "user": "",
        "passwd": "",
        "database": config.get("SQL", "database"),
    }

    cm = ConnectionManager(cm_config)
    ui = UserInterface(cm)
    try:
        ui.start()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
