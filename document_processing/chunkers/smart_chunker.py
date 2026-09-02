"""智能分块：把长文本切成适合向量化的小块"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class SmartChunker:
    """把 Document 列表切分为 chunk，并给每块编号（chunk_index）。"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # RecursiveCharacterTextSplitter = "递归切分器"
        # 先按段落切，段落还太长就按句子切，句子还太长就按词切……
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,  # 每块目标长度（字符数）
            chunk_overlap=chunk_overlap,  # 相邻块重叠长度
            # 分隔符优先级：中文优先按段落、句子切，避免从词中间切断
            separators=["\n\n", "\n", "。", ".", "！", "？", " ", ""],
        )

    def chunk(self, documents: list[Document]) -> list[Document]:
        result = []
        chunk_index = 0

        for doc in documents:
            chunks = self._splitter.split_documents([doc])  # 切这一篇文档
            for chunk in chunks:
                chunk.metadata["chunk_index"] = chunk_index  # 给每块贴编号
                chunk_index += 1
                result.append(chunk)
        return result
