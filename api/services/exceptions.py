class UserServiceExc(BaseException):
    pass


class UserAlreadyExists(UserServiceExc):

    def __init__(self, username: bool, email: bool):
        self.username = username
        self.email = email


class UserNotExists(UserServiceExc):
    pass


class InvalidUsernameLen(UserServiceExc):
    pass


class InvalidPasswordLen(UserServiceExc):
    pass


class InvalidEmail(UserServiceExc):
    pass
