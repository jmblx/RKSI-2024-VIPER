from typing import AsyncIterable

from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import Uow
from infrastructure.db.uow import SAUnitOfWork


class UowProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=Uow)
    async def provide_session(self, session: AsyncSession) -> SAUnitOfWork:
        return SAUnitOfWork(session)
