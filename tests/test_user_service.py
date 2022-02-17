import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.config import TestDatabase
from api.database.base import Base
from api.models.users import UnregisteredUser

from api.services.user import UserService


uname, email, password = 'test_user', 'test_mail@gmail.com', '123123'

fake_users = [
    UnregisteredUser(username=f"{uname}_{i}", email=f"{email}_{i}", password='123123')
    for i in range(5)
]


engine = create_async_engine(
        f'mysql+aiomysql://{TestDatabase.USER}:{TestDatabase.PASSWORD}@'
        f'{TestDatabase.HOST}:{TestDatabase.PORT}/{TestDatabase.NAME}', echo=True
)
s_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

        yield s_maker()


@pytest_asyncio.fixture
async def user_service(db_session) -> UserService:
    async with UserService(db_session) as s:
        yield s


@pytest_asyncio.fixture
async def service_with_dataset(db_session) -> UserService:
    async with UserService(db_session) as s:

        for fake_user in fake_users:
            await s.create(fake_user)

        yield s


@pytest.mark.asyncio
async def test_read_empty(user_service: UserService):
    assert await user_service.get_all() == []


@pytest.mark.asyncio
async def test_create_user(user_service: UserService):
    await user_service.create(UnregisteredUser(username=uname, email=email, password=password))
    assert all(await user_service.is_exists(email=email, username=uname))


@pytest.mark.asyncio
async def test_user_exists_email(user_service: UserService):

    await user_service.create(UnregisteredUser(username=uname, email=email, password='123123'))
    _, email_ex = await user_service.is_exists('uname_that_not_exists', email)

    assert email_ex


@pytest.mark.asyncio
async def test_user_exists_username(user_service: UserService):

    await user_service.create(UnregisteredUser(username=uname, email=email, password='123123'))
    uname_ex, _ = await user_service.is_exists(uname, 'email_that_not_exists')

    assert uname_ex


@pytest.mark.asyncio
async def test_bulk_insert(service_with_dataset):
    assert len(await service_with_dataset.get_all()) == 5


@pytest.mark.asyncio
async def test_delete_users(service_with_dataset):
    for user_data in await service_with_dataset.get_all():
        user_controller = await service_with_dataset.get_controller(user_data.id)
        await user_controller.delete()

    assert len(await service_with_dataset.get_all()) == 0


if __name__ == "__main__":
    pytest.main()
