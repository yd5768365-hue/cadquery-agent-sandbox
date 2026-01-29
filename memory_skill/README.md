# Memory Skill for CAE Agent

## 概述
这是一个为CAE智能体设计的记忆系统，能够记住对话内容并在后续对话中提供上下文支持。

## 功能特性
- 持久化对话记忆
- 上下文关联
- 知识提取与总结
- 记忆检索与查询
- 支持外部记忆模型API

## 文件结构
```
memory_skill/
├── __init__.py
├── memory_manager.py    # 核心记忆管理器
├── conversation_memory.py # 对话记忆处理
├── knowledge_extractor.py # 知识提取
├── memory_retriever.py   # 记忆检索
├── storage.py           # 存储抽象层
├── api_integration.py    # 外部API集成
└── config.py            # 配置文件
```

## 使用方法

### 基本使用
```python
from memory_skill.memory_manager import MemoryManager

# 初始化记忆管理器
memory_manager = MemoryManager()

# 记录对话
memory_manager.remember_conversation(
    user_input="用户输入",
    agent_response="智能体回复",
    context="当前上下文"
)

# 检索相关记忆
relevant_memories = memory_manager.retrieve_relevant_memories(
    current_query="当前问题"
)
```

### 配置外部API
```python
# 在config.py中配置
MEMORY_API_CONFIG = {
    "api_endpoint": "https://your-memory-api.com",
    "api_key": "your-api-key",
    "model_name": "your-memory-model",
    "max_tokens": 1000,
    "temperature": 0.7
}
```

## 记忆类型

### 1. 对话记忆 (Conversation Memory)
- 记录用户与智能体的完整对话
- 包含时间戳、上下文信息
- 支持多轮对话关联

### 2. 知识记忆 (Knowledge Memory)
- 从对话中提取的关键知识
- 概念、定义、公式等结构化信息
- 支持知识图谱关联

### 3. 项目记忆 (Project Memory)
- 项目进展、决策过程
- 代码变更、问题解决记录
- 学习进度和里程碑

### 4. 个性化记忆 (Personal Memory)
- 用户偏好、学习风格
- 常见问题和解决方案
- 个性化建议历史

## API接口

### 记忆存储API
```python
async def store_memory(
    content: str,
    memory_type: str,
    metadata: dict = None,
    tags: list = None
) -> str:
    """
    存储记忆内容
    
    Args:
        content: 记忆内容
        memory_type: 记忆类型 (conversation, knowledge, project, personal)
        metadata: 元数据信息
        tags: 标签列表
    
    Returns:
        memory_id: 记忆ID
    """
```

### 记忆检索API
```python
async def retrieve_memories(
    query: str,
    memory_type: str = None,
    limit: int = 10,
    threshold: float = 0.7
) -> list:
    """
    检索相关记忆
    
    Args:
        query: 查询内容
        memory_type: 记忆类型过滤
        limit: 返回结果数量限制
        threshold: 相关性阈值
    
    Returns:
        相关记忆列表
    """
```

### 记忆更新API
```python
async def update_memory(
    memory_id: str,
    content: str = None,
    metadata: dict = None,
    tags: list = None
) -> bool:
    """
    更新记忆内容
    
    Args:
        memory_id: 记忆ID
        content: 新内容
        metadata: 新元数据
        tags: 新标签
    
    Returns:
        更新是否成功
    """
```

## 集成到CAE智能体

### 1. 初始化记忆系统
```python
# 在CAE智能体初始化时
from memory_skill.memory_manager import MemoryManager

class CAEAgent:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.conversation_history = []
```

### 2. 对话处理流程
```python
async def process_message(self, user_input: str) -> str:
    # 1. 检索相关记忆
    relevant_memories = await self.memory_manager.retrieve_relevant_memories(user_input)
    
    # 2. 生成响应（考虑记忆上下文）
    context = self._build_context(relevant_memories)
    response = await self._generate_response(user_input, context)
    
    # 3. 存储对话记忆
    await self.memory_manager.remember_conversation(
        user_input=user_input,
        agent_response=response,
        context=context
    )
    
    return response
```

### 3. 知识提取
```python
async def extract_knowledge(self, conversation: dict) -> list:
    """
    从对话中提取知识要点
    """
    knowledge_points = await self.memory_manager.knowledge_extractor.extract(conversation)
    
    for knowledge in knowledge_points:
        await self.memory_manager.store_memory(
            content=knowledge['content'],
            memory_type='knowledge',
            metadata=knowledge['metadata'],
            tags=knowledge['tags']
        )
    
    return knowledge_points
```

## 配置选项

### 基本配置
```python
MEMORY_CONFIG = {
    "storage_type": "file",  # file, database, api
    "max_memory_size": 10000,
    "retention_days": 365,
    "auto_extract": True,
    "similarity_threshold": 0.7
}
```

### 外部API配置
```python
EXTERNAL_API_CONFIG = {
    "enabled": True,
    "endpoint": "https://api.memory-service.com",
    "model": "memory-embedding-v1",
    "api_key": "your-api-key",
    "timeout": 30,
    "retry_count": 3
}
```

## 使用建议

### 1. 记忆管理策略
- 定期清理过期记忆
- 建立记忆重要性评分
- 实现记忆压缩和归档

### 2. 隐私保护
- 敏感信息过滤
- 用户数据加密
- 记忆访问权限控制

### 3. 性能优化
- 记忆索引优化
- 缓存热点记忆
- 异步处理机制

## 扩展功能

### 1. 记忆可视化
- 记忆关系图谱
- 知识演化时间线
- 个性化记忆报告

### 2. 智能遗忘
- 基于重要性的记忆衰减
- 冗余记忆去重
- 过期记忆自动清理

### 3. 跨会话记忆
- 用户身份识别
- 长期记忆维护
- 个性化档案构建

这个记忆系统将使CAE智能体能够：
- 记住用户的偏好和学习风格
- 维护项目进展的连续性
- 提供个性化和上下文相关的建议
- 从历史对话中学习和改进