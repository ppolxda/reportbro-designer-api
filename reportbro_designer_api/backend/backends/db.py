# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:54:46.

@author: ppolxda

@desc: sql Api
"""
from contextlib import asynccontextmanager
from functools import partial
from functools import wraps
from inspect import signature
from typing import Awaitable
from typing import Callable
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import load_only

from .. import models as mm
from .. import schemas as sa
from .base import BackendBase


def session_begin(session_maker: async_sessionmaker[AsyncSession]):
    """事务上下文管理."""
    __session_maker = session_maker

    @asynccontextmanager
    async def _session_begin():
        async with __session_maker() as session:
            try:
                assert isinstance(session, AsyncSession)
                yield session
            except Exception as ex:
                await session.rollback()
                raise ex
            else:
                await session.commit()

    return _session_begin


def find_filed_idx(field: str, func: Callable[..., Awaitable]) -> int:
    """Find session index in function call parameter."""
    func_params = signature(func).parameters
    try:
        # func_params is an ordered dict -- this is the "recommended" way of getting the position
        session_args_idx = tuple(func_params).index(field)
    except ValueError:
        raise ValueError(
            f"Function {func.__qualname__} has no `{field}` argument"
        ) from None

    return session_args_idx


find_session_idx = partial(find_filed_idx, "session")
RT = TypeVar("RT")


def provide_db(func: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
    """参数动态注入装饰器."""
    session_args_idx = find_session_idx(func)

    @wraps(func)
    async def wrapper(self: "DBBackend", *args, **kwargs) -> RT:
        if "session" in kwargs or session_args_idx < len(args):
            return await func(self, *args, **kwargs)
        else:
            async with self.session_begin() as session:
                return await func(self, *args, session=session, **kwargs)

    return wrapper


class DBBackendClient(object):
    """DBBackendClient."""

    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession],
        project: str = "default",
        default_template: Optional[dict] = None,
        query_max_limit: int = 1000,
    ):
        """init."""
        super().__init__()
        if default_template is None:
            default_template = {}

        self.project_name = project
        self.async_session = async_session
        self.default_template = default_template
        self.session_begin = session_begin(self.async_session)
        self.query_max_limit = query_max_limit

    @provide_db
    async def _clean_all(self, session: Optional[AsyncSession] = None):
        """Clean database, This api only use for test."""
        assert session
        for tbl in reversed(mm.Base.metadata.sorted_tables):
            await session.execute(delete(tbl))
            await session.commit()

    @provide_db
    async def _get_template_list(
        self,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> List[sa.TemplateInfo]:
        """Get templates."""
        query = (
            select(mm.Templates)
            .options(
                load_only(
                    mm.Templates.created_at,
                    mm.Templates.updated_at,
                    mm.Templates.tid,
                    mm.Templates.version_id,
                    mm.Templates.template_name,
                    mm.Templates.template_type,
                    mm.Templates.project,
                )
            )
            .order_by(mm.Templates.created_at.desc())
            .limit(min(limit, self.query_max_limit))
            .offset(offset)
        )
        query = self.pick_condition(
            query, tid, version_id, project, template_name, template_type
        )
        assert session
        results = await session.execute(query)
        return [sa.TemplateInfo.from_orm(i) for i in results.scalars()]

    @provide_db
    async def _get_templates_version_list(
        self,
        tid: str,
        project: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> List[sa.TemplateInfo]:
        query = (
            select(mm.TemplatesVersion)
            .options(
                load_only(
                    mm.TemplatesVersion.created_at,
                    mm.TemplatesVersion.updated_at,
                    mm.TemplatesVersion.tid,
                    mm.TemplatesVersion.version_id,
                    mm.TemplatesVersion.template_name,
                    mm.TemplatesVersion.template_type,
                    mm.TemplatesVersion.project,
                )
            )
            .order_by(mm.TemplatesVersion.created_at.desc())
            .limit(min(limit, self.query_max_limit))
            .offset(offset)
        )
        query = self.pick_condition(
            query, tid, None, project, None, None, class_=mm.TemplatesVersion
        )

        assert session
        results = await session.execute(query)
        return [sa.TemplateInfo.from_orm(i) for i in results.scalars()]

    @provide_db
    async def _is_template_exist(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Get templates."""
        query = select(mm.Templates.tid).limit(1)
        query = self.pick_condition(query, tid, version_id, project)

        assert session
        results = await session.execute(query)
        tmpl = results.scalars().first()
        return True if tmpl else False

    @provide_db
    async def _get_template(
        self,
        tid: str,
        project: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        lock: bool = False,
    ) -> Optional[mm.Templates]:
        """Get templates."""
        query = select(mm.Templates).limit(1)
        query = self.pick_condition(query, tid, None, project)
        if lock:
            query = query.with_for_update()

        assert session
        results = await session.execute(query)
        tmp = results.scalars().first()
        if not tmp:
            return None
        return tmp

    @provide_db
    async def _get_template_version(
        self,
        tid: str,
        version_id: str,
        project: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        lock: bool = False,
    ) -> Optional[mm.TemplatesVersion]:
        """Get templates."""
        query = select(mm.TemplatesVersion).limit(1)
        query = self.pick_condition(
            query, tid, version_id, project, class_=mm.TemplatesVersion
        )
        if lock:
            query = query.with_for_update()

        assert session
        results = await session.execute(query)
        tmp = results.scalars().first()
        if not tmp:
            return None
        return tmp

    @provide_db
    async def _lock_template_versions(
        self,
        tid: str,
        project: str,
        session: Optional[AsyncSession] = None,
    ) -> List[mm.TemplatesVersion]:
        """Get templates."""
        query = (
            select(mm.TemplatesVersion)
            .options(
                load_only(
                    mm.TemplatesVersion.created_at, mm.TemplatesVersion.version_id
                )
            )
            .where(
                mm.TemplatesVersion.tid == tid,
                mm.TemplatesVersion.project == project,
            )
            .with_for_update()
        )

        assert session
        results = await session.execute(query)
        return [i for i in results.scalars()]

    def pick_condition(
        self,
        query,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        class_: Union[Type[mm.Templates], Type[mm.TemplatesVersion]] = mm.Templates,
    ):
        """Pick template Query conndition."""
        if tid:
            query = query.where(class_.tid == tid)

        if not project:
            project = self.project_name

        if project:
            query = query.where(class_.project == project)

        if version_id:
            query = query.where(class_.version_id == version_id)

        if template_name:
            query = query.where(class_.template_name == template_name)

        if template_type:
            query = query.where(class_.template_type == template_type)
        return query

    @provide_db
    async def _put_template(
        self,
        tid: str,
        version_id: str,
        template_name: str,
        template_type: str,
        report: dict,
        project: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> sa.BaseTemplateId:
        """Put templates."""
        assert session
        # 更新或创建template
        project = self.project_name if not project else project
        add_list: List[Union[mm.TemplatesVersion, mm.Templates]] = [
            mm.TemplatesVersion(
                tid=tid,
                version_id=version_id,
                project=project,
                template_name=template_name,
                template_type=template_type,
                template_config=report,
            ),
        ]
        templage = await self._get_template(tid, session=session, lock=True)
        if templage:
            templage.project = project
            templage.version_id = version_id
            templage.template_name = template_name
            templage.template_type = template_type
            templage.template_config = report

        else:
            add_list.append(
                mm.Templates(
                    tid=tid,
                    version_id=version_id,
                    project=project,
                    template_name=template_name,
                    template_type=template_type,
                    template_config=report,
                )
            )

        session.add_all(add_list)
        return sa.BaseTemplateId(
            tid=tid,
            version_id=version_id,
        )

    @provide_db
    async def _delete_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Delete templates version."""
        assert session
        project = self.project_name if not project else project
        # if tid not exist, do not anything
        template = await self._get_template(
            tid, project=project, lock=True, session=session
        )
        if not template:
            return

        if version_id:
            query = delete(mm.TemplatesVersion).where(
                mm.TemplatesVersion.tid == tid,
                mm.TemplatesVersion.version_id == version_id,
                mm.TemplatesVersion.project == project,
            )
            await session.execute(query)

            versions = await self._lock_template_versions(tid, project, session=session)
            versions = sorted(
                iter(i for i in versions if i.version_id != version_id),
                key=lambda x: x.created_at,
            )

            # if version table empty, all file deleted
            if versions:
                last_version = await self._get_template_version(
                    tid, versions[-1].version_id, project=project, session=session
                )
                assert last_version
                template.version_id = last_version.version_id
                template.template_type = last_version.template_type
                template.template_name = last_version.template_name
                template.template_config = last_version.template_config

            else:
                query = delete(mm.Templates).where(
                    mm.Templates.tid == tid,
                    mm.Templates.project == project,
                )
                await session.execute(query)

        else:
            query = delete(mm.TemplatesVersion).where(
                mm.TemplatesVersion.tid == tid,
                mm.TemplatesVersion.project == project,
            )
            await session.execute(query)

            query = delete(mm.Templates).where(
                mm.Templates.tid == tid,
                mm.Templates.project == project,
            )
            await session.execute(query)


class DBBackend(DBBackendClient, BackendBase):
    """DBBackend."""

    async def clean_all(self):
        """Clean database, This api only use for test."""
        await self._clean_all()

    async def is_template_exist(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> bool:
        """Is templates Exist."""
        project = self.project_name if not project else project
        r = await self._is_template_exist(tid, version_id, project)
        return r

    async def get_templates_list(
        self,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates list."""
        project = self.project_name if not project else project
        r = await self._get_template_list(
            tid, version_id, project, template_name, template_type, limit, offset
        )
        return r

    async def get_templates_version_list(
        self,
        tid: str,
        project: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates version list."""
        project = self.project_name if not project else project
        r = await self._get_templates_version_list(tid, project, limit, offset)
        return r

    async def get_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Optional[sa.TemplateConfigInfo]:
        """Get templates."""
        project = self.project_name if not project else project
        if version_id:
            r = await self._get_template_version(tid, version_id, project)
        else:
            r = await self._get_template(tid, project)

        if not r:
            return None

        y = sa.TemplateConfigInfo.from_orm(r)
        y.report = r.template_config if r.template_config else {}
        return y

    async def put_template(
        self,
        template_name: str,
        template_type: str,
        report: dict,
        tid: Optional[str] = None,
        project: Optional[str] = None,
    ) -> sa.BaseTemplateId:
        """Put templates."""
        if not report:
            if self.default_template:
                report = self.default_template
            else:
                report = {}

        if tid is None:
            tid = await self.gen_uuid_object_key(project=project)

        # 创建template
        version_id = self.gen_uuid()
        project = self.project_name if not project else project
        r = await self._put_template(
            tid, version_id, template_name, template_type, report, project
        )
        return r

    async def delete_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ):
        """Delete templates version."""
        project = self.project_name if not project else project
        r = await self._delete_template(tid, version_id, project)
        return r
