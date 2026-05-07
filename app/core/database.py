from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

class DatabaseHelper:
    def __init__(self):
        self.engine = None
        self.async_session_factory = None

    def init(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        is_test: bool = False,
    ):

        engine_kwargs = {
            "url": url,
            "echo": echo,
            "echo_pool": echo_pool,
        }

        if is_test:
            engine_kwargs["poolclass"] = NullPool
        else:
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow

        self.engine = create_async_engine(**engine_kwargs)

        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self):
        if self.engine:
            await self.engine.dispose()

    async def session_getter(self):
        async with self.async_session_factory() as session:
            yield session

db_helper = DatabaseHelper()