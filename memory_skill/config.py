"""
记忆系统配置文件
"""

# 基本配置
MEMORY_CONFIG = {
    "storage_type": "file",  # file, database, api
    "max_memory_size": 10000,
    "retention_days": 365,
    "auto_extract": True,
    "similarity_threshold": 0.7,
    "memory_directory": "memory_storage"
}

# 记忆类型配置
MEMORY_TYPES = {
    "conversation": {
        "description": "对话记忆",
        "retention_days": 90,
        "max_size": 5000
    },
    "knowledge": {
        "description": "知识记忆",
        "retention_days": 365,
        "max_size": 10000
    },
    "project": {
        "description": "项目记忆",
        "retention_days": 365,
        "max_size": 8000
    },
    "personal": {
        "description": "个性化记忆",
        "retention_days": 365,
        "max_size": 3000
    }
}

# 外部API配置
EXTERNAL_API_CONFIG = {
    "enabled": False,  # 默认关闭，用户可自行开启
    "endpoint": "https://api.memory-service.com",
    "model": "memory-embedding-v1",
    "api_key": "",  # 用户需要提供自己的API密钥
    "timeout": 30,
    "retry_count": 3,
    "batch_size": 10
}

# 知识提取配置
KNOWLEDGE_EXTRACTION_CONFIG = {
    "enabled": True,
    "min_confidence": 0.6,
    "extract_keywords": True,
    "extract_concepts": True,
    "extract_formulas": True,
    "max_knowledge_per_conversation": 5
}

# 记忆检索配置
RETRIEVAL_CONFIG = {
    "max_results": 10,
    "similarity_threshold": 0.5,
    "time_decay_factor": 0.95,
    "boost_recent": True,
    "boost_important": True
}

# 隐私保护配置
PRIVACY_CONFIG = {
    "filter_sensitive_info": True,
    "encrypt_personal_data": True,
    "anonymize_user_data": True,
    "data_retention_policy": "strict"
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    "cache_enabled": True,
    "cache_size": 1000,
    "cache_ttl": 3600,  # 1小时
    "index_enabled": True,
    "async_processing": True
}

# 调试配置
DEBUG_CONFIG = {
    "log_level": "INFO",
    "log_memory_operations": True,
    "log_api_calls": False,
    "save_debug_info": False
}