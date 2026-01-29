"""
外部API集成模块
支持用户提供的记忆模型API
"""

import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExternalMemoryAPI:
    """外部记忆API集成"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.endpoint = config.get("endpoint", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "memory-embedding-v1")
        self.timeout = config.get("timeout", 30)
        self.retry_count = config.get("retry_count", 3)
        self.batch_size = config.get("batch_size", 10)
        
        # 会话管理
        self.session = None
        self.last_used = None
        
        if not self.enabled:
            logger.info("外部记忆API未启用")
            return
        
        if not self.endpoint:
            logger.warning("外部记忆API端点未配置")
            self.enabled = False
            return
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self.enabled:
            await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _ensure_session(self):
        """确保会话存在"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {}
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
    
    async def store_memory(
        self,
        memory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """通过API存储记忆"""
        if not self.enabled:
            return {"error": "API未启用"}
        
        try:
            await self._ensure_session()
            
            # 准备请求数据
            request_data = {
                "model": self.model,
                "memory": memory_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # 发送请求
            async with self.session.post(
                f"{self.endpoint}/memories",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"记忆存储成功: {result.get('id', 'unknown')}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"记忆存储失败: {response.status} - {error_text}")
                    return {"error": f"API错误: {response.status}"}
        
        except Exception as e:
            logger.error(f"记忆存储异常: {e}")
            return {"error": str(e)}
    
    async def retrieve_memory(
        self,
        memory_id: str
    ) -> Dict[str, Any]:
        """通过API检索记忆"""
        if not self.enabled:
            return {"error": "API未启用"}
        
        try:
            await self._ensure_session()
            
            async with self.session.get(
                f"{self.endpoint}/memories/{memory_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"记忆检索失败: {response.status} - {error_text}")
                    return {"error": f"API错误: {response.status}"}
        
        except Exception as e:
            logger.error(f"记忆检索异常: {e}")
            return {"error": str(e)}
    
    async def search_memories(
        self,
        query: str,
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """通过API搜索记忆"""
        if not self.enabled:
            return []
        
        try:
            await self._ensure_session()
            
            # 准备请求数据
            request_data = {
                "model": self.model,
                "query": query,
                "limit": limit,
                "filters": filters or {}
            }
            
            async with self.session.post(
                f"{self.endpoint}/memories/search",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    memories = result.get("memories", [])
                    logger.info(f"搜索到 {len(memories)} 个记忆")
                    return memories
                else:
                    error_text = await response.text()
                    logger.error(f"记忆搜索失败: {response.status} - {error_text}")
                    return []
        
        except Exception as e:
            logger.error(f"记忆搜索异常: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """通过API更新记忆"""
        if not self.enabled:
            return {"error": "API未启用"}
        
        try:
            await self._ensure_session()
            
            async with self.session.put(
                f"{self.endpoint}/memories/{memory_id}",
                json=updates
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"记忆更新成功: {memory_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"记忆更新失败: {response.status} - {error_text}")
                    return {"error": f"API错误: {response.status}"}
        
        except Exception as e:
            logger.error(f"记忆更新异常: {e}")
            return {"error": str(e)}
    
    async def delete_memory(
        self,
        memory_id: str
    ) -> Dict[str, Any]:
        """通过API删除记忆"""
        if not self.enabled:
            return {"error": "API未启用"}
        
        try:
            await self._ensure_session()
            
            async with self.session.delete(
                f"{self.endpoint}/memories/{memory_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"记忆删除成功: {memory_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"记忆删除失败: {response.status} - {error_text}")
                    return {"error": f"API错误: {response.status}"}
        
        except Exception as e:
            logger.error(f"记忆删除异常: {e}")
            return {"error": str(e)}
    
    async def batch_store_memories(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量存储记忆"""
        if not self.enabled:
            return [{"error": "API未启用"} for _ in memories]
        
        results = []
        
        # 分批处理
        for i in range(0, len(memories), self.batch_size):
            batch = memories[i:i + self.batch_size]
            
            try:
                await self._ensure_session()
                
                # 准备请求数据
                request_data = {
                    "model": self.model,
                    "memories": batch,
                    "timestamp": datetime.now().isoformat()
                }
                
                async with self.session.post(
                    f"{self.endpoint}/memories/batch",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        batch_results = await response.json()
                        results.extend(batch_results)
                        logger.info(f"批量存储成功: {len(batch)} 个记忆")
                    else:
                        error_text = await response.text()
                        error_result = {"error": f"API错误: {response.status}"}
                        results.extend([error_result] * len(batch))
                        logger.error(f"批量存储失败: {response.status} - {error_text}")
            
            except Exception as e:
                logger.error(f"批量存储异常: {e}")
                error_result = {"error": str(e)}
                results.extend([error_result] * len(batch))
        
        return results
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        if not self.enabled:
            return {"error": "API未启用"}
        
        try:
            await self._ensure_session()
            
            async with self.session.get(
                f"{self.endpoint}/memories/statistics"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"获取统计信息失败: {response.status} - {error_text}")
                    return {"error": f"API错误: {response.status}"}
        
        except Exception as e:
            logger.error(f"获取统计信息异常: {e}")
            return {"error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        if not self.enabled:
            return {"status": "disabled", "message": "API未启用"}
        
        try:
            await self._ensure_session()
            
            async with self.session.get(
                f"{self.endpoint}/health"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "message": "API连接正常",
                        "details": result
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"API连接失败: {response.status}"
                    }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"API连接异常: {str(e)}"
            }

class APIStorageAdapter:
    """API存储适配器 - 实现存储接口"""
    
    def __init__(self, api_config: Dict[str, Any]):
        self.api = ExternalMemoryAPI(api_config)
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """存储记忆"""
        async with self.api:
            result = await self.api.store_memory(memory_data)
            if "error" not in result:
                return result.get("id", "")
            else:
                raise Exception(result["error"])
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """检索记忆"""
        async with self.api:
            result = await self.api.retrieve_memory(memory_id)
            if "error" not in result:
                return result
            else:
                logger.error(f"检索记忆失败: {result['error']}")
                return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆"""
        async with self.api:
            memories = await self.api.search_memories(query, limit)
            return memories
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        async with self.api:
            result = await self.api.update_memory(memory_id, updates)
            if "error" not in result:
                return True
            else:
                logger.error(f"更新记忆失败: {result['error']}")
                return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        async with self.api:
            result = await self.api.delete_memory(memory_id)
            if "error" not in result:
                return True
            else:
                logger.error(f"删除记忆失败: {result['error']}")
                return False

# 使用示例
async def example_usage():
    """API使用示例"""
    # 配置API
    api_config = {
        "enabled": True,
        "endpoint": "https://your-memory-api.com",
        "api_key": "your-api-key",
        "model": "memory-embedding-v1",
        "timeout": 30,
        "retry_count": 3,
        "batch_size": 10
    }
    
    # 创建API实例
    async with ExternalMemoryAPI(api_config) as api:
        # 测试连接
        health_check = await api.test_connection()
        print(f"API连接状态: {health_check}")
        
        # 存储记忆
        memory_data = {
            "type": "conversation",
            "content": "这是一个测试记忆",
            "tags": ["测试", "示例"]
        }
        
        store_result = await api.store_memory(memory_data)
        print(f"存储结果: {store_result}")
        
        # 搜索记忆
        search_results = await api.search_memories("测试记忆")
        print(f"搜索结果: {len(search_results)} 个记忆")
        
        # 获取统计信息
        stats = await api.get_memory_statistics()
        print(f"统计信息: {stats}")

if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())