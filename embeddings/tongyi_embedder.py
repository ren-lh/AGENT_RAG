"""通义向量化封装
为什么需要重试？
调用云端 API 偶尔网络抖动/限流，
指数退避重试（1秒 → 2秒 → 4秒，最多 3 次）
"""
import logging
import time

import dashscope

from dashscope import TextEmbedding
from core.config import settings

logger = logging.getLogger(__name__)


class TongyiEmbedder:
    """封装 DashScope text-embedding-v4：批量向量化 + 查询向量化 + 重试。"""

    MAX_RETRIES = 3  # 最多重试 3 次

    def __init__(self) -> None:
        # dashscope SDK 的惯例：设一次全局 Key，之后所有调用都生效
        dashscope.api_key = settings.dashscope_api_key

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量向量化文档文本（上传入库时用），返回与输入等长的向量列表。

        注意：入库用 text_type="document"，与查询用的 "query" 区分开。
        模型会针对两种场景分别优化向量表达，混用会降低检索准确度。
        """
        return self._call_with_retry(texts, text_type="document")

    def embed_query(self, text: str) -> list[float]:
        """向量化单条查询文本（检索时用），返回一个向量。"""
        return self._call_with_retry([text], text_type="query")[0]

    def _call_with_retry(self, texts: list[str], text_type: str) -> list[list[float]]:
        """调用 DashScope 接口，失败时指数退避重试。"""
        delay = 1  # 第一次失败后等一秒
        last_exc: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                resp = TextEmbedding.call(
                    model=settings.tongyi_embedding_model,
                    input=texts,
                    text_type=text_type,
                    dimension=settings.vector_size,
                )

                # DashScope 返回 status_code != 200 表示失败（code/message 里有原因）
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"DashScope error {resp.code}: {resp.message}"
                    )

                # 响应里 output.embeddings 是 [{embedding, text_index}, ...]
                # 按 text_index 排序，保证返回顺序和输入顺序一致
                embeddings = sorted(
                    resp.output["embeddings"],
                    key=lambda item: item["text_index"],
                )
                return [item["embedding"] for item in embeddings]

            except Exception as exc:
                last_exc = exc
                if attempt < self.MAX_RETRIES - 1:  # 还没到最大次数，等一下再试
                    logger.warning(
                        "Embedding attempt %d/%d failed: %s. Retrying in %ds...",
                        attempt + 1, self.MAX_RETRIES, exc, delay,
                    )
                    time.sleep(delay)
                    delay *= 2  # 退避：1 → 2 → 4

        raise last_exc  # 3 次都失败，把最后一次异常抛出去（注意：必须在 for 循环外面）
