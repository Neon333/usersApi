from typing import List, Union, Tuple

from database.base import get_session
from models.users import RegisteredUser, UnregisteredUser, UpdateUser
from database.models import User

from sqlalchemy import select, update
from sqlalchemy.sql.functions import func

from services.base import RequireDbService
from services.exceptions import UserAlreadyExists, InvalidEmail, InvalidUsernameLen, InvalidPasswordLen, UserNotExists

from email_validator import validate_email, EmailNotValidError

from utlis.password import hash_password


class UserController(RequireDbService):

    def __init__(self, user_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = user_id

    async def _get_instance(self) -> User:
        return await self._db_session.get(User, self._id)

    async def update(self, updates: dict):
        """
        Updates user attributes. Available listed in UserService.AVAILABLE_UPDATES
        :param updates:
        :return:
        """

        if 'password' in updates:
            updates['password'] = hash_password(updates['password'])

        await self._db_session.execute(update(User).where(User.id == self._id).values(updates))
        await self._db_session.commit()

    async def delete(self):
        """
        Deletes current user from database
        :return:
        """
        await self._db_session.delete(await self._get_instance())
        await self._db_session.commit()


class UserService(RequireDbService):

    AVAILABLE_UPDATES = ['email', 'username', 'password']

    USERNAME_LEN_MIN, USERNAME_LEN_MAX = 6, 32
    PASSWORD_LEN_MIN, PASSWORD_LEN_MAX = 8, 32

    async def is_exists(self, username: str, email: str) -> Tuple[bool, bool]:
        """
        Checks is user with same username or email exists in database

        :returns: Tuple with 2 elements where first element indicates is username exists and second is email exists
        :rtype: tuple
        """
        username_exists_stmt = select(User).filter(func.lower(User.username) == username.lower())
        email_exists_stmt = select(User).filter(func.lower(User.email) == email.lower())

        return (await self._db_session.execute(username_exists_stmt)).first() is not None, \
               (await self._db_session.execute(email_exists_stmt)).first() is not None

    async def create(self, user_data: UnregisteredUser) -> int:
        """
        Creates user and returns new user id on success
        :returns: new user id
        :rtype: int
        :raises: UserAlreadyExists if username or email already in user
        """
        exists_result = await self.is_exists(user_data.username, user_data.email)

        if any(exists_result):
            raise UserAlreadyExists(*exists_result)

        user_data.password = hash_password(user_data.password)

        new_user = User(**user_data.dict())
        self._db_session.add(new_user)
        await self._db_session.commit()

        return new_user.id

    @classmethod
    def prepare_update_data(cls, update_data: UpdateUser) -> dict:
        return {k: v for k, v in update_data.dict().items() if v is not None and k in cls.AVAILABLE_UPDATES}

    def validate_update_data(self, updates: dict):

        updates_map = {
            'email': (updates.get('email', None), self.__validate_email, InvalidEmail),
            'username': (updates.get('username', None), self.__validate_uname_len, InvalidUsernameLen),
            'password': (updates.get('password', None), self.__validate_password_len, InvalidPasswordLen),
        }

        for update_key, update_data in updates_map.items():
            new_value, call_validator, exc_class = update_data
            if new_value is not None and not call_validator(new_value):
                raise exc_class

    def validate_user_data(self, user_data: UnregisteredUser):
        if not self.__validate_email(user_data.email):
            raise InvalidEmail
        elif not self.__validate_uname_len(user_data.username):
            raise InvalidUsernameLen
        elif not self.__validate_password_len(user_data.password):
            raise InvalidPasswordLen

    def __validate_uname_len(self, username: str) -> bool:
        return self.USERNAME_LEN_MIN <= len(username) <= self.USERNAME_LEN_MAX

    def __validate_password_len(self, username: str) -> bool:
        return self.PASSWORD_LEN_MIN <= len(username) <= self.PASSWORD_LEN_MAX

    @classmethod
    def __validate_email(cls, email: str) -> bool:
        try:
            validate_email(email)
        except EmailNotValidError:
            return False
        else:
            return True

    async def get(self, user_id: int) -> Union[RegisteredUser, None]:
        user_instance = await self._db_session.get(User, ident=user_id)
        return RegisteredUser(
            id=user_instance.id, username=user_instance.email, email=user_instance.email,
            register_date=user_instance.register_date
        ) if user_instance is not None else None

    async def get_all(self) -> List[RegisteredUser]:
        """Returns all registered users"""
        users = (await self._db_session.execute(select(User))).scalars()
        return [
            RegisteredUser(
                id=user.id, username=user.username, email=user.email, register_date=user.register_date
            ) for user in users
        ]

    async def get_controller(self, user_id: int) -> UserController:
        if not await self.get(user_id):
            raise UserNotExists

        return UserController(user_id=user_id, current_session=self._db_session)


def inject_user_service() -> UserService:
    return UserService(current_session=get_session())
