import asyncio
import os

import aiomysql
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """从 .env 读取 MySQL 配置"""
    mysql_host:str = os.getenv('MYSQL_HOST')
    mysql_port:int = int(os.getenv('MYSQL_PORT'))
    mysql_user:str = os.getenv('MYSQL_USER')
    mysql_password:str = os.getenv('MYSQL_PASSWORD')
    mysql_db:str = os.getenv('MYSQL_DB')

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


async def main():
    settings = Settings()

    # 1. 建立异步连接（连到 ragagent 库）
    conn = await aiomysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        db=settings.mysql_db,
    )

    # 2. 执行最简单的 SQL，验证连通
    async with conn.cursor() as cur:
        await cur.execute("SELECT 1")
        result = await cur.fetchone()
        print("MySQL 查询结果:", result)

    conn.close()
    print("MySQL 验证通过")


asyncio.run(main())