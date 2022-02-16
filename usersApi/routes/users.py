from typing import List, Union

import config
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.encoders import jsonable_encoder

from models.responses import UserCreatedSuccess, EmailAlreadyInUse, UsernameAlreadyInUse, UserCreationFail, \
    InvalidUsername, InvalidPassword, InvalidEmail
from models.users import RegisteredUser, UnregisteredUser, UpdateUser
from services.exceptions import UserAlreadyExists, InvalidUsernameLen, InvalidPasswordLen, \
    InvalidEmail as InvalidEmailExc, UserNotExists

from services.user import UserService, inject_user_service, UserController

users_router = APIRouter(prefix=config.API_PATH)


RESPONSE_EXC_MAP = {
    InvalidUsernameLen: InvalidUsername,
    InvalidPasswordLen: InvalidPassword,
    InvalidEmailExc: InvalidEmail,
}


def validate_user_data(data: Union[dict, UnregisteredUser], user_service: UserService):

    validator = user_service.validate_update_data if isinstance(data, dict) else user_service.validate_user_data
    validation_response = None

    try:
        validator(data)
    except (InvalidUsernameLen, InvalidPasswordLen, InvalidEmailExc) as e:
        validation_response = RESPONSE_EXC_MAP.get(e.__class__, None)
    finally:
        return validation_response


async def get_user_controller(user_id: int, user_service: UserService) -> UserController:
    try:
        user_controller = await user_service.get_controller(user_id)
    except UserNotExists:
        raise HTTPException(status_code=404)
    else:
        return user_controller


@users_router.get('/user/{user_id}', response_model=RegisteredUser)
async def get_user(user_id: int, users: UserService = Depends(inject_user_service)):
    async with users as user_service:

        user = await user_service.get(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail='Invalid user id')

        return user


@users_router.get('/user-list', response_model=List[RegisteredUser], status_code=200)
async def get_users(users: UserService = Depends(inject_user_service)):
    async with users as user_service:
        return await user_service.get_all()


@users_router.post('/user', status_code=201)
async def create_user(user_data: UnregisteredUser, response: Response, users: UserService = Depends(inject_user_service)):
    async with users as user_service:

        validation_response = validate_user_data(data=user_data, user_service=user_service)
        if validation_response is not None:
            return jsonable_encoder(validation_response().dict())

        try:
            user_id = await user_service.create(user_data)
        except UserAlreadyExists as e:

            errors = []
            if e.email:
                errors.append(EmailAlreadyInUse())
            if e.username:
                errors.append(UsernameAlreadyInUse())

            fail_response = UserCreationFail()
            [fail_response + e for e in errors]

            return jsonable_encoder(fail_response.dict())
        else:
            return jsonable_encoder(UserCreatedSuccess(id=user_id).dict())


@users_router.delete('/user/{user_id}', status_code=204)
async def delete_user(user_id: int, users: UserService = Depends(inject_user_service)):
    async with users as user_service:

        user_controller = await get_user_controller(user_id, user_service)
        await user_controller.delete()
        return Response(status_code=204)


@users_router.put('/user/{user_id}')
async def user_full_update(user_id: int, user_data: UnregisteredUser, users: UserService = Depends(inject_user_service)):
    async with users as user_service:

        user_controller = await get_user_controller(user_id, user_service)

        validation_response = validate_user_data(data=user_data, user_service=user_service)
        if validation_response is not None:
            return jsonable_encoder(validation_response().dict())

        await user_controller.update(user_data.dict())

        return Response(status_code=204)


@users_router.patch('/user/{user_id}')
async def user_update(user_id: int, user_data: UpdateUser, users: UserService = Depends(inject_user_service)):
    async with users as user_service:

        user_controller = await get_user_controller(user_id, user_service)

        prepared_updates = user_service.prepare_update_data(user_data)
        validation_response = validate_user_data(data=prepared_updates, user_service=user_service)

        if validation_response is not None:
            return jsonable_encoder(validation_response().dict())

        await user_controller.update(prepared_updates)
        return Response(status_code=204)

