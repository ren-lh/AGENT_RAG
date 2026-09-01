import uuid

from langchain_core.documents import Document
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType

from core.config import settings


class MilvusStore:
    """封装 Milvus 向量库操作：建 collection、MD5 查重、写入、删除、检索。"""

    def __init__(self, client: MilvusClient) -> None:
        self._client = client

    # schema设计
    def _build_schema(self, vector_size: int) -> CollectionSchema:
        """设计 Milvus 表结构"""
        fields = [
            # 主键：自己生成的 uuid 字符串
            FieldSchema(name='id', dtype=DataType.VARCHAR, is_primary=True, max_length=64),
            # 向量字段：维度必须和 Embedding 模型一致
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_size),
            # 文本字段：chunk 原文。max_length 留 2 倍余量防 chunk 略超
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=settings.chunk_size * 2),
            # 以下都是"元数据字段"
            FieldSchema(name="file_md5", dtype=DataType.VARCHAR, max_length=32),  # 文件指纹，去重用
            FieldSchema(name="collection", dtype=DataType.VARCHAR, max_length=64),  # 知识库名
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),  # 入库时间
            FieldSchema(name="chunk_index", dtype=DataType.INT64),  # 块序号
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),  # 来源文件名
            FieldSchema(name="file_type", dtype=DataType.VARCHAR, max_length=32),  # 文件格式
            FieldSchema(name="row", dtype=DataType.INT64),  # CSV 行号，非 CSV 用 -1
        ]
        return CollectionSchema(fields=fields, auto_id=False, enable_dynamic_field=False)

    # 创建 collection
    def ensure_collection(self, collection: str) -> None:
        """若 collection 不存在则自动创建（带 schema）。"""
        if not self._client.has_collection(collection):
            self._client.create_collection(
                collection_name=collection,
                schema=self._build_schema(vector_size=settings.vector_size),
            )

    # MD5 查重
    def md5_exists(self, file_md5: str, collection: str) -> bool:
        """检查该 MD5 是否已在 collection 中存在（去重判断）。"""
        try:
            rows = self._client.query(
                collection_name=collection,
                filter=f'file_md5 == "{file_md5}"',
                output_fields=["id"],
                limit=1,
            )
            return len(rows) > 0
        except Exception:
            return False

    # 写入
    def upsert(self, chunks: list[Document], vectors: list[list[float]], collection: str) -> None:
        """将 chunks 和 vectors 批量写入 Milvus。"""
        self.ensure_collection(collection)
        data = []

        for chunk, vector in zip(chunks, vectors):
            # 把 chunk 的 metadata 平铺成 schema 里定义的字段
            data.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "text": chunk.page_content,
                "file_md5": chunk.metadata.get("file_md5", ""),
                "collection": chunk.metadata.get("collection", collection),
                "created_at": chunk.metadata.get("created_at", ""),
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "source": chunk.metadata.get("source", ""),
                "file_type": chunk.metadata.get("file_type", ""),
                "row": chunk.metadata.get("row", -1),
            })

        self._client.insert(collection_name=collection, data=data)

    #  删除
    def delete_by_md5(self, file_md5: str, collection: str) -> int:
        """删除 collection 中所有匹配该 MD5 的实体，返回删除数量。
        Milvus 直接按 filter 表达式删，一步到位。
        """
        try:
            deleted = self._client.delete(
                collection_name=collection,
                filter=f'file_md5 == "{file_md5}"',
            )
            return len(deleted) if deleted else 0
        except Exception:
            return 0

    # 检索
    def search(self, query_vector, collection, top_k, score_threshold) -> list[dict]:
        """语义检索，返回相似度高于阈值的 top-k 结果。
        Milvus 的 COSINE distance = 余弦相似度（越大越像，范围 [-1, 1]），
        search_params 里的 radius 是"下界"：只保留 distance >= radius 的结果
        """
        try:
            response = self._client.search(
                collection_name=collection,
                data=[query_vector],
                limit=top_k,
                output_fields=["text", "file_md5", "source", "chunk_index", "created_at", "file_type"],
                search_params={"params": {"radius": score_threshold}},
            )
        except Exception:
            # collection 不存在或其他检索异常，返回空结果
            return []

        results = []
        for hits in response:  # 注意：response 是"外层列表套内层列表"
            for hit in hits:  # 每个 hit: {"id", "distance", "entity"}
                entity = hit.get("entity", {})  # entity 里是 schema 字段
                results.append({
                    "content": entity.get("text", ""),
                    "source": entity.get("source", ""),
                    "score": hit.get("distance", 0.0),
                    "metadata": {k: v for k, v in entity.items() if k != "text"},
                })
        return results

    # 列出所有 collection
    def list_collections(self) -> list[str]:
        """列出所有 collection 名称。"""
        return self._client.list_collections()
