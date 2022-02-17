API_VERSION = 'v1'
API_PATH = f'/api/{API_VERSION}'


class Database:
    USER = "root"
    PASSWORD = "kolanchik2015"
    NAME = "usersApi"
    HOST = "127.0.0.1"


class TestDatabase(Database):
    NAME = "usersApi_test"
    PORT = 3306
