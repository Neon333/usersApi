from typing import List

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool
    errors: List[str] = []

    def __add__(self, other):
        other_errors = getattr(other, 'errors', [])
        self.errors += other_errors

        return self


class UserCreatedSuccess(BaseResponse):
    id: int
    success = True


class UserCreationFail(BaseResponse):
    success = False


class EmailAlreadyInUse(UserCreationFail):
    errors: List[str] = ['Email already in use']


class UsernameAlreadyInUse(UserCreationFail):
    errors: List[str] = ['Username already in use']


class InvalidUsername(UserCreationFail):
    errors: List[str] = ['Username must be from 6 to 32 characters']


class InvalidEmail(UserCreationFail):
    errors: List[str] = ['Invalid email address']


class InvalidPassword(UserCreationFail):
    errors: List[str] = ['Password must be from 8 to 32 characters']