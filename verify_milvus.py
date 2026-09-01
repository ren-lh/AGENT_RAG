from pymilvus import MilvusClient
# 创建 milvus lite 本地数据库
client = MilvusClient("milvus_lite.db")
# 创建 collection（类比：数据库里的"表"），指定向量维度 8

COLLECTION = "test_collection"
client.create_collection(collection_name=COLLECTION,dimension=8)

# 插入一条数据：id + 向量 + 附带文字字段
client.insert(
    COLLECTION,
[{"id": 1, "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], "text": "hello milvus lite"}],
)

# 检索
results = client.search(
    COLLECTION,
    data=[[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]],
    limit=1,
    output_fields=["text"],
)
print("检索结果:", results)


# 5. 清理：删掉 collection（验证完不留垃圾）
client.drop_collection(COLLECTION)
print("Milvus Lite 验证通过")