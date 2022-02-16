from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    pass


class RequireDbService(BaseService):

    def __init__(self, current_session: AsyncSession):
        self._db_session = current_session

    async def close_session(self):
        await self._db_session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
