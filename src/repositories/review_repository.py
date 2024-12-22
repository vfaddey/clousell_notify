from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Review


class ReviewRepository(ABC):
    @abstractmethod
    def create(self, review):
        raise NotImplementedError

    @abstractmethod
    def get_by_provider(self, provider_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    def get_by_plan(self, pricing_plan_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    def update(self, review):
        raise NotImplementedError

    @abstractmethod
    def delete(self, review_id: int | UUID):
        raise NotImplementedError


class SqlaReviewRepository(ReviewRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, review: Review) -> Review:
        try:
            self._session.add(review)
            await self._session.commit()
            await self._session.refresh(review)
            return review
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    async def get_by_provider(self, provider_id: UUID):
        stmt = select(Review).where(Review.provider_id == provider_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_plan(self, pricing_plan_id: UUID):
        stmt = select(Review).where(Review.pricing_plan_id == pricing_plan_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, review: Review) -> Review:
        try:
            self._session.add(review)
            await self._session.commit()
            await self._session.refresh(review)
            return review
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

    async def delete(self, review_id) -> Review:
        try:
            stmt = delete(Review).where(Review.id == review_id).returning(Review)
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.scalar()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e

