# 全局配置模块所有的可配置项集中在这里，通过.env覆盖
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    工作机制（重要）：
    - 每个字段写一个"字面量默认值"；
    - pydantic-settings 会自动去 .env / 环境变量里找同名变量并覆盖默认值；
    - 例如字段 mysql_host 会自动读取环境变量 MYSQL_HOST（大小写不敏感）。
    - 所以 .env 里有就用 .env 的值，没有就用默认值，永远不会缺。
    """
    # Milvus 向量数据库
    # Lite 模式：填本地 .db 文件路径
    # 生产切 Docker 版 Milvus，只需改成 "http://localhost:19530"，其他代码不用动
    milvus_address: str = "milvus_lite.db"
    # 默认知识库名称（上传文档时不指定 collection 就用它）
    default_collection: str = "default"
    # MySQL（会话记忆 + 对话日志）
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "ragagent"

    # 上传限制
    max_upload_size_mb: int = 50

    # 相似度阈值；低于这个值的不会被返回，值越高越严格
    score_threshold: float = 0.7
    # 默认返回结果数量
    top_k: int = 5

    # 向量维度
    vector_size: int = 1536

    # =====文档分块参数=====
    # 每个 chunk最大字符数
    chunk_size: int = 1000
    # 相邻 chunk的重贴字符数
    chunk_overlap: int = 200
    # 扫码 PDF 判断阈值：解析后字符数低于此值视为扫描件
    min_text_length_for_scanned_detection: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
