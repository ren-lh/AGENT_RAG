"""
所有格式加载器的抽象基类。

什么是"抽象基类"？类比：一张"职位说明书"。
它规定每个 loader 必须会两件事（load + supported_extensions），
但自己不写具体逻辑，让每个子类（TXT/PDF/...）各自实现。
"""
from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class BaseLoader(ABC):
    """所有格式加载器的抽象基类。"""

    @abstractmethod
    def load(self, file_path: Path) -> list[Document]:
        """加载文件，返回 Document 列表。

        每个子类实现自己的解析逻辑：
        - TextLoader：读文本
        - PDFLoader：解析 PDF
        ...
        """
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """这个加载器支持哪些文件后缀（含点，如 {'.txt', '.TXT'}）。"""
        ...
