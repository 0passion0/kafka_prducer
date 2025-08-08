MONGODB_DATABASES = {
    "default": {
        "type": "mongodb",
        'user': 'admin',
        'password': r'StrongP@ssw0rd',
        'auth_source': 'admin',  # 认证数据库（必须与用户创建库一致）
        'host': '47.92.65.175',
        'port': 27017,
        'database': 'tlg',
        "charset": "utf8mb4"
    },
}

PRODUCER_CONFIG = {
    # Kafka 集群地址列表（ip:port）
    "bootstrap_servers": ['127.0.0.1:19092', '127.0.0.1:19096', '127.0.0.1:19100'],
    # 消息压缩方式
    "compression_type": "gzip",
    # 发送失败时的重试次数
    "retries": 5,
    # 多少个副本确认后才算发送成功：
    #   0：不等待确认（最快，可能丢数据）
    #   1：只等 leader 确认（折中）
    #   all/-1：等所有 ISR 副本确认（最安全，最慢）
    "acks": 1,
    # 一批消息的字节数阈值，达到该大小或超过 linger_ms 就立即发送
    "batch_size": 512 * 1024,  # 16 KB
    # 消息在客户端缓冲区最多等待多少毫秒再发送（与 batch_size 配合做微批）
    "linger_ms": 100,

}

DEFAULT_CURSOR_FILE_PATH = 'runtime/cursors/mongodb'
