# 数据库配置
MYSQL_DATABASES = {
    "xxx": {
        "type": "mysql",
        'user': 'medpeer',
        'password': 'medpeer',
        'host': '192.168.1.245',
        'port': 3306,
        'database': 'raw_data',
        "charset": "utf8mb4"
    },
    "default": {
        "type": "mysql",
        'user': 'root',
        'password': 'Btlg2002',
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'info',
        "charset": "utf8mb4"
    },
    "default1": {
        "type": "mysql",
        'user': 'root',
        'password': 'Btlg2002',
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'nfsc',
        "charset": "utf8mb4"
    },
}


MONGODB_DATABASES = {
    "default": {
        "type": "mongodb",
        'user': 'medpeer',
        'password': 'medpeer',
        'auth_source': 'admin',  # 认证数据库（必须与用户创建库一致）
        'host': '192.168.1.245',
        'port': 27017,
        'database': 'raw_data',
        "charset": "utf8mb4"
    },
    "my": {
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
    "bootstrap_servers": ['180.76.250.147:19092', '180.76.250.147:19096', '180.76.250.147:19100'],
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
    "linger_ms": 1000,

}
# ElasticSearch数据库连接
ELASTIC_CONNECTION = [
    {
        # 连接标识
        "sign": "default",
        # 服务器地址
        'host': ['192.168.1.245'],
        # 账号
        "user": "elastic_db",
        # 密码
        "password": "medpeer",
        # 连接协议
        "scheme": "http",
        # 服务器端口
        'port': 9200,
        # 超时时间（秒）
        "timeout": 30,
        # 错误重试次数
        "max_retries": 3,
        # 超时是否重试
        "retry_on_timeout": True,
    },
]