-- ========== 表 1：会话消息表==========
-- 一个 session_id 下挂一串消息（human=用户 / ai=助手）
CREATE TABLE IF NOT EXISTS session_messages (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,  -- 流水号（自增主键）
    session_id  VARCHAR(64)  NOT NULL,              -- 会话标识
    role        VARCHAR(16)  NOT NULL,              -- human / ai
    content     TEXT         NOT NULL,              -- 消息内容
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 时间
    -- 索引：按会话查历史时，用 (session_id + created_at) 快速定位
    INDEX idx_session_time (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- utf8mb4：支持中文和 emoji（utf8 不够用）

-- ========== 表 2：对话日志表==========
-- 每一轮完整的 问+答+出处，永久留档
CREATE TABLE IF NOT EXISTS conversations (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,  -- 流水号
    session_id  VARCHAR(64) NOT NULL,               -- 会话标识
    query       TEXT        NOT NULL,               -- 用户问题
    answer      TEXT        NOT NULL,               -- 助手回答
    sources     JSON        NULL,                   -- 出处（存 JSON 数组）
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)                  -- 按会话查日志
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;