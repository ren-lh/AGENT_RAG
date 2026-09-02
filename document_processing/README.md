| 文件                        | 作用                                     |
|-----------------------------|------------------------------------------|
| `loaders/base.py`           | 所有 loader 的「职位说明书」（抽象基类） |
| `loaders/text_loader.py`    | TXT 解析（自动检测编码）                 |
| `cleaners/text_cleaner.py`  | 清洗噪声                                 |
| `chunkers/smart_chunker.py` | 智能切块                                 |
| `pipeline.py`               | 串联 + 注入元数据                        |