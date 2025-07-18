import pandas as pd
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Sequence

from sqlalchemy import Boolean
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select as sqlalchemy_select
from sqlalchemy.orm import Mapped, selectinload, load_only
from sqlalchemy.sql import select, update as sqlalchemy_update

from ...db.models.mapped_columns import *
from .enum import BillStatus
from ...core.psql import async_db_session, Base


T = TypeVar("T")


class ModelAdmin(Generic[T]):
    
    class DoesNotExists(Exception):
        pass

    @classmethod
    async def create(cls, **kwargs) -> T:
        """
        # Создает новый объект и возвращает его.
        :param kwargs: Поля и значения для объекта.
        :return: Созданный объект.
        """

        async with async_db_session() as session:
            obj = cls(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def add(cls, **kwargs) -> None:
        """
        # Создает новый объект.
        :param kwargs: Поля и значения для объекта.
        """

        async with async_db_session() as session:
            session.add(cls(**kwargs))
            await session.commit()

    async def update(self, **kwargs) -> T:
        """
        Обновляет текущий объект в базе и возвращает его заново (с актуальными данными).

        :param kwargs: Поля и значения, которые надо обновить.
        :return: Обновлённый объект
        """
        async with async_db_session() as session:
            stmt = sqlalchemy_update(self.__class__).where(
                self.__class__.id == self.id
            ).values(**kwargs)

            await session.execute(stmt)
            await session.commit()

            # Заново получаем объект из базы
            result = await session.execute(
                sqlalchemy_select(self.__class__).where(self.__class__.id == self.id)
            )
            updated_obj = result.scalar_one_or_none()

            return updated_obj

    async def delete(self) -> None:
        """
        # Удаляет объект.
        """
        async with async_db_session() as session:
            await session.delete(self)
            await session.commit()

    @classmethod
    async def get(cls, select_in_load: str | None = None, **kwargs) -> T:
        """
        # Возвращает одну запись, которая удовлетворяет введенным параметрам.

        :param select_in_load: Загрузить сразу связанную модель.
        :param kwargs: Поля и значения.
        :return: Объект или вызовет исключение DoesNotExists.
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        try:
            async with async_db_session() as session:
                results = await session.execute(query)
                (result,) = results.one()
                return result
        except NoResultFound:
            return None

    @classmethod
    async def get_first(cls, select_in_load: str | None = None, **kwargs) -> T | None:
        """
        Возвращает первую запись, удовлетворяющую условиям. 
        Безопасный аналог get(): не выбрасывает исключений при множественных результатах или их отсутствии.

        :param select_in_load: Имя связанной модели для подгрузки (если нужно).
        :param kwargs: Параметры фильтрации по полям модели.
        :return: Первая подходящая запись или None.
        """
        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query = query.options(selectinload(getattr(cls, select_in_load)))

        async with async_db_session() as session:
            results = await session.execute(query)
            row = results.first()
            if row:
                return row[0]
            return None

    @classmethod
    async def filter(cls, select_in_load: str | None = None, **kwargs) -> Sequence[T]:
        """
        # Возвращает все записи, которые удовлетворяют фильтру.

        :param select_in_load: Загрузить сразу связанную модель.
        :param kwargs: Поля и значения.
        :return: Перечень записей.
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        try:
            async with async_db_session() as session:
                results = await session.execute(query)
                return results.scalars().all()
        except NoResultFound:
            return ()

    @classmethod
    async def all(
            cls, select_in_load: str = None, values: list[str] = None
    ) -> Sequence[T]:
        """
        # Получает все записи.

        :param select_in_load: Загрузить сразу связанную модель.
        :param values: Список полей, которые надо вернуть, если нет, то все (default None).
        """

        if values and isinstance(values, list):
            # Определенные поля
            values = [getattr(cls, val) for val in values if isinstance(val, str)]
            query = select(cls).options(load_only(*values))
        else:
            # Все поля
            query = select(cls)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        async with async_db_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def exclude(cls, select_in_load: str | None = None, **kwargs) -> Sequence[T]:
        """
        # Возвращает все записи, которые не удовлетворяют фильтру (то есть, исключает значения).
        :param select_in_load: Загрузить сразу связанную модель.
        :param kwargs: Поля и значения для исключения.
        :return: Перечень записей.
        """
        # Строим условия для исключения (не равно)
        params = [getattr(cls, key) != val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        async with async_db_session() as session:
            result = await session.execute(query)
            return result.scalars().all()


# Хранение списка актуальных подписок
class Users(Base, ModelAdmin):
    
    __tablename__ = 'users'

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str | None]
    role: Mapped[str] = mapped_column(
        default='user',
        comment='Роль пользователя'
    )
    order: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Были ли заказы'
    )
    ref_links: Mapped[str | None] =  mapped_column(
        default=None,
        comment='Реф. ссылка, по которой перешёл пользователь'
    )
    date_registration: Mapped[datetime] = mapped_column(default=now_moscow)

    @classmethod
    async def get_users_without_orders(cls) -> pd.DataFrame:
        """
        Возвращает DataFrame с пользователями у которых order=False и role='user'.
        Поля: tg_id, name, role, date_registration
        """
        async with async_db_session() as session:
            stmt = select(cls).where(cls.order == False, cls.role == 'user')
            result = await session.execute(stmt)
            users = result.scalars().all()

            data = [
                {
                    "Telegram ID": u.tg_id,
                    "Имя": u.name,
                    "Роль": u.role,
                    "Реф. ссылка": u.ref_links,
                    "Дата регистрации": u.date_registration
                }
                for u in users
            ]

            return pd.DataFrame(data)


# Хранение списка реф. ссылок
class ReferralLinks(Base, ModelAdmin):
    
    __tablename__ = 'referral_links'

    id: Mapped[intpk]
    referral_link: Mapped[str] = mapped_column(unique=True)
    number_users: Mapped[int] = mapped_column(default=0)
    date_creation: Mapped[datetime] = mapped_column(default=now_moscow)


# Хранение всех заявок
class OrderUsers(Base, ModelAdmin):
    
    __tablename__ = 'order_users'

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str | None]
    price: Mapped[float | None] = mapped_column(Float)
    image_size: Mapped[str | None]
    copies_count: Mapped[str | None]
    phone_number: Mapped[str | None]
    geolocation: Mapped[str | None]
    file_id: Mapped[str | None]
    file_type: Mapped[str | None]
    pickup: Mapped[str | None]
    dispatch_status: Mapped[str | None] = mapped_column(
        default='not_sent',
        comment='Статус отправки менеджером: not_sent/sent'
    )
    last_id_message_group: Mapped[int | None]
    last_update: Mapped[datetime] = mapped_column(default=now_moscow)


# Хранение всех счетов
class Bill(Base, ModelAdmin):
    
    __tablename__ = 'bill'

    id: Mapped[intpk]
    bill_id: Mapped[str] = mapped_column(unique=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[BillStatus] = mapped_column(default=BillStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=now_moscow)