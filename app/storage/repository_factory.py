from app.storage.database_config import close_db_config


class RepositoryFactory:
    async def close(self) -> None:
        await close_db_config()


# Global repository factory instance
repository_factory = RepositoryFactory()
