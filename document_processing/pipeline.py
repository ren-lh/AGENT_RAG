"""
员工手册.txt
   │  loader（按后缀选解析器）
   ▼
原始文本（可能是 GBK/UTF-8 编码）
   │  cleaner（洗掉噪声字符）
   ▼
干净文本
   │  chunker（切成 1000 字一块，重叠 200 字）
   ▼
chunk1 / chunk2 / chunk3 ...
   │  pipeline（给每块贴标签）
   ▼
带 file_md5 / collection / chunk_index / created_at 的 chunk 列表 →（M3b 向量化入库）

文档处理流水线：loader → cleaner → chunker → 带元数据的 chunk 列表。
"""
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.documents import Document

from .cleaners.text_cleaner import TextCleaner
from .chunkers.smart_chunker import SmartChunker
from .loaders.base import BaseLoader
from .loaders.text_loader import TextLoader

from core.config import settings


def _build_loader_registry() -> dict[str, BaseLoader]:
    """把每个 loader 注册到它支持的后缀上（后缀 → loader 的映射表）。
    这样 pipeline 只需要"按后缀查表"，不用写一堆 if/elif。
    """
    registry: dict[str, BaseLoader] = {}
    for loader in [TextLoader()]:  # 先只注册 txt，后续 加 PDF/Word/MD/CSV
        for ext in loader.supported_extensions:
            registry[ext] = loader
    return registry


_LOADERS: dict[str, BaseLoader] = _build_loader_registry()


def get_loader(extension: str) -> BaseLoader:
    """根据文件后缀返回对应 loader，不支持的格式抛 ValueError。"""
    loader = _LOADERS.get(extension)
    if not loader:
        raise ValueError(f"Unsupported file extension: {extension}")
    return loader


class DocumentPipeline:
    """串联 loader → cleaner → chunker，把文件转成带元数据的 chunk 列表。"""

    def __init__(self, cleaner=None, chunker=None):
        # 允许外部传入自定义 cleaner/chunker（方便测试），默认用标准版
        self._cleaner = cleaner or TextCleaner()
        self._chunker = chunker or SmartChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    def process(self, file_path: Path, file_md5: str, collection: str) -> list[Document]:
        """完整处理流程：load → clean → chunk → 注入元数据。"""
        loader = get_loader(file_path.suffix)  # 1. 按后缀选 loader
        docs = loader.load(file_path)  # 2. 解析出原始文本

        # 早失败：空文档直接报错（不浪费后续步骤）
        total_text = " ".join(d.page_content for d in docs).strip()
        if not total_text:
            raise ValueError(f"未在'{file_path.name}'中找到可提取的文本")

        cleaned = self._cleaner.clean(docs)  # 3. 清洗
        chunks = self._chunker.chunk(cleaned)  # 4. 切块

        # 5. 给每个 chunk 注入元数据：文件指纹 / 知识库 / 入库时间
        now = datetime.now(timezone.utc).isoformat()
        for chunk in chunks:
            chunk.metadata.update(
                {
                    "file_md5": file_md5,
                    "collection": collection,
                    "created_at": now,
                }
            )

        return chunks
