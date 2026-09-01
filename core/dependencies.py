"""依赖注入：全局单例的"总闸"。

FastAPI 的依赖注入机制：
接口函数在参数里写 Depends(get_store)，FastAPI 就自动调用 get_store()，
把建好的对象"递"进来。接口自己不 new 对象，统一来这里领。

@lru_cache：函数第一次调用后结果被缓存，之后直接返回缓存
            → 整个进程只有一个实例（单例）。
"""
from functools import lru_cache

from pymilvus import MilvusClient

from core.config import settings


@lru_cache
def get_milvus_client() -> MilvusClient:
    """返回 Milvus client 单例（懒加载：第一次被用到才创建）。"""
    return MilvusClient(uri=settings.milvus_address)


@lru_cache
def get_store():
    # 返回MilvusStored单例
    from vectorstore.milvus_store import MilvusStore
    return MilvusStore(client=get_milvus_client())
