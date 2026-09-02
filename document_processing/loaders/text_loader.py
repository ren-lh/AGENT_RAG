"""TXT 文本加载器：自动检测编码（UTF-8 / GBK 等）。

为什么需要编码检测？
中文电脑上的 txt 可能是 GBK（Windows）或 UTF-8（Mac/Linux），
直接按 UTF-8 解码 GBK 文件会乱码，所以要先用 chardet 猜一下。
"""
from pathlib import Path

import chardet
from langchain_core.documents import Document

from .base import BaseLoader


class TextLoader(BaseLoader):
    """加载 .txt 文件 """

    @property
    def supported_extensions(self) -> set[str]:
        return {".txt", ".TXT"}  # 大小写都支持

    def load(self, file_path: Path) -> list[Document]:
        # 读原始字节
        raw = file_path.read_bytes()
        # chardet 自动检测编码（返回 {'encoding': 'GB2312', ...} 之类）
        detected = chardet.detect(raw)
        encoding = detected.get('encoding') or 'utf-8'  # 检测不到就默认 UTF-8

        # 按检测到的编码解码；errors="replace" 遇到解不动的字符用 � 代替，不崩
        text = raw.decode(encoding, errors="replace")

        # 包成 Document 返回（page_content=正文，metadata=来源信息）
        return [
            Document(
                page_content=text,
                metadata={"source": file_path.name, "file_type": "txt"},
            )
        ]
