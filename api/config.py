API_VERSION = 'v1'
API_PATH = f'/api/{API_VERSION}'


class Database:
    USER = "root"
    PASSWORD = "usersApi"
    NAME = "usersApi"
    HOST = "db"


class TestDatabase(Database):
    NAME = "usersApi_test"
    PORT = 3307
    HOST = "test_db"
