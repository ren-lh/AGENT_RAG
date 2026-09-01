"""MySQL 异步连接池（全局唯一）"""
import aiomysql

from core.config import settings

_pool = None  # 模块级变量：整个进程共享同一个连接池


async def get_pool() -> aiomysql.Pool:
    """获取（或首次创建）MySQL 连接池单例。"""
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_db,
            autocommit=True,  # 每条 SQL 自动提交，不用手动 commit
            minsize=1,  # 池里最少保留 1 个连接
            maxsize=5,  # 最多 5 个
            charset="utf8mb4",  # 支持中文
        )
    return _pool
