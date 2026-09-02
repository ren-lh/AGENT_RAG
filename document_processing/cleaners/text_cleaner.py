"""文本清洗：去掉噪声字符、规范化空白、过滤空行。

为什么要清洗？
从文件里解析出来的文本常夹带"垃圾"：隐形控制字符、多余空格、
全空白行。这些会干扰切块和向量化效果，先洗干净。
"""
from langchain_core.documents import Document
import re


class TextCleaner:
    """清洗文档文本。"""

    def clean(self, documents: list[Document]) -> list[Document]:
        """对每个 Document 清洗，返回新的 Document 列表。"""
        return [self._clean_doc(doc) for doc in documents]

    def _clean_doc(self, doc: Document) -> Document:
        text = doc.page_content

        # 1. 去掉 null 字节（\x00）和 DEL 字符（\x7f）——"隐形垃圾"
        text = re.sub(r"[\x00\x7f]", "", text)

        # 2. 其他控制字符（保留换行 \n 和制表符 \t）替换成空格
        text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", " ", text)

        # 3. 多个连续空格/Tab 合并成一个空格
        text = re.sub(r"[ \t]+", " ", text)

        # 4. 逐行处理：
        #    - 真正空行：保留（连续多个只留一个，避免段落被拉开）
        #    - 只含空白的行：删除（它没有内容）
        #    - 有内容的行：去掉首尾空白后保留
        lines = text.split("\n")
        result_lines = []
        prev_empty = False
        for line in lines:
            stripped = line.strip()
            if line == "":  # 真正空行
                if not prev_empty:
                    result_lines.append("")
                prev_empty = True
            elif stripped == "":  # 只含空白：丢弃
                pass
            else:  # 有内容：strip 后保留
                result_lines.append(stripped)
                prev_empty = False

        # 5. 去掉开头和结尾的空行
        while result_lines and result_lines[0] == "":
            result_lines.pop(0)
        while result_lines and result_lines[-1] == "":
            result_lines.pop()

        text = "\n".join(result_lines)

        # 返回新 Document（保留原 metadata 不变）
        return Document(page_content=text, metadata=doc.metadata)
