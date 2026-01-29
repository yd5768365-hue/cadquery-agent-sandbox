"""
记忆管理器 - 记忆系统的核心组件
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from .config import (
    MEMORY_CONFIG, MEMORY_TYPES, EXTERNAL_API_CONFIG,
    KNOWLEDGE_EXTRACTION_CONFIG, RETRIEVAL_CONFIG
)
from .storage import get_storage
from .conversation_memory import ConversationMemory
from .knowledge_extractor import KnowledgeExtractor
from .memory_retriever import MemoryRetriever

logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器 - 统一管理所有记忆操作"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or MEMORY_CONFIG
        
        # 初始化存储
        self.storage = get_storage(
            storage_type=self.config.get("storage_type", "file"),
            storage_dir=self.config.get("memory_directory", "memory_storage")
        )
        
        # 初始化组件
        self.conversation_memory = ConversationMemory(self.storage)
        self.knowledge_extractor = KnowledgeExtractor()
        self.memory_retriever = MemoryRetriever(self.storage)
        
        # 记忆统计
        self.memory_stats = {
            "total_memories": 0,
            "by_type": {k: 0 for k in MEMORY_TYPES.keys()},
            "last_cleanup": datetime.now().isoformat()
        }
        
        # 启动后台任务
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 记忆清理任务
        asyncio.create_task(self._cleanup_old_memories())
        
        # 记忆统计更新任务
        asyncio.create_task(self._update_memory_stats())
    
    async def _cleanup_old_memories(self):
        """清理过期记忆"""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # 每天执行一次
                
                cutoff_date = datetime.now() - timedelta(days=self.config.get("retention_days", 365))
                await self._cleanup_memories_before(cutoff_date)
                
                logger.info("记忆清理任务完成")
                
            except Exception as e:
                logger.error(f"记忆清理任务失败: {e}")
    
    async def _update_memory_stats(self):
        """更新记忆统计"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时更新一次
                
                stats = await self._calculate_memory_stats()
                self.memory_stats.update(stats)
                
                logger.info(f"记忆统计更新: {stats}")
                
            except Exception as e:
                logger.error(f"记忆统计更新失败: {e}")
    
    async def _cleanup_memories_before(self, cutoff_date: datetime):
        """清理指定日期之前的记忆"""
        # 这里需要根据存储类型实现具体的清理逻辑
        # 暂时留空，等待具体实现
        pass
    
    async def _calculate_memory_stats(self) -> Dict[str, Any]:
        """计算记忆统计信息"""
        # 这里需要根据存储类型实现具体的统计逻辑
        # 暂时返回默认值
        return {
            "total_memories": 0,
            "by_type": {k: 0 for k in MEMORY_TYPES.keys()},
            "last_cleanup": datetime.now().isoformat()
        }
    
    # ===== 对话记忆管理 =====
    
    async def remember_conversation(
        self,
        user_input: str,
        agent_response: str,
        context: Dict[str, Any] = None,
        tags: List[str] = None,
        importance: float = 1.0
    ) -> str:
        """记录对话记忆"""
        try:
            # 创建对话记忆
            conversation_data = {
                "type": "conversation",
                "user_input": user_input,
                "agent_response": agent_response,
                "context": context or {},
                "tags": tags or [],
                "importance": importance,
                "timestamp": datetime.now().isoformat()
            }
            
            # 存储对话记忆
            memory_id = await self.storage.store_memory(conversation_data)
            
            # 自动提取知识
            if KNOWLEDGE_EXTRACTION_CONFIG.get("enabled", True):
                await self._extract_and_store_knowledge(conversation_data)
            
            logger.info(f"对话记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储对话记忆失败: {e}")
            raise
    
    async def get_conversation_history(
        self,
        limit: int = 10,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """获取对话历史"""
        try:
            # 构建查询条件
            query = "type:conversation"
            if start_date:
                query += f" created_at:>={start_date.isoformat()}"
            if end_date:
                query += f" created_at:<={end_date.isoformat()}"
            
            # 搜索记忆
            memories = await self.storage.search_memories(query, limit)
            
            # 按时间排序
            memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    # ===== 知识记忆管理 =====
    
    async def store_knowledge(
        self,
        content: str,
        knowledge_type: str = "general",
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        source: str = None
    ) -> str:
        """存储知识记忆"""
        try:
            knowledge_data = {
                "type": "knowledge",
                "content": content,
                "knowledge_type": knowledge_type,
                "metadata": metadata or {},
                "tags": tags or [],
                "source": source,
                "created_at": datetime.now().isoformat(),
                "confidence": metadata.get("confidence", 1.0) if metadata else 1.0
            }
            
            memory_id = await self.storage.store_memory(knowledge_data)
            
            logger.info(f"知识记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储知识记忆失败: {e}")
            raise
    
    async def _extract_and_store_knowledge(self, conversation_data: Dict[str, Any]):
        """从对话中提取并存储知识"""
        try:
            # 合并对话内容
            full_text = f"{conversation_data.get('user_input', '')} {conversation_data.get('agent_response', '')}"
            
            # 提取知识
            knowledge_points = await self.knowledge_extractor.extract(full_text)
            
            # 存储知识
            for knowledge in knowledge_points:
                await self.store_knowledge(
                    content=knowledge["content"],
                    knowledge_type=knowledge["type"],
                    metadata=knowledge.get("metadata", {}),
                    tags=knowledge.get("tags", []),
                    source=f"conversation:{conversation_data.get('id', 'unknown')}"
                )
            
            logger.info(f"从对话中提取了 {len(knowledge_points)} 个知识点")
            
        except Exception as e:
            logger.error(f"知识提取失败: {e}")
    
    async def search_knowledge(
        self,
        query: str,
        knowledge_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索知识记忆"""
        try:
            # 构建查询条件
            search_query = f"type:knowledge {query}"
            if knowledge_type:
                search_query += f" knowledge_type:{knowledge_type}"
            
            # 搜索记忆
            memories = await self.storage.search_memories(search_query, limit)
            
            # 按置信度和时间排序
            memories.sort(key=lambda x: (
                x.get("confidence", 0),
                x.get("created_at", "")
            ), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"搜索知识记忆失败: {e}")
            return []
    
    # ===== 项目记忆管理 =====
    
    async def store_project_memory(
        self,
        event_type: str,
        description: str,
        details: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> str:
        """存储项目记忆"""
        try:
            project_data = {
                "type": "project",
                "event_type": event_type,
                "description": description,
                "details": details or {},
                "tags": tags or [],
                "timestamp": datetime.now().isoformat(),
                "version": details.get("version", "1.0.0") if details else "1.0.0"
            }
            
            memory_id = await self.storage.store_memory(project_data)
            
            logger.info(f"项目记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储项目记忆失败: {e}")
            raise
    
    async def get_project_timeline(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取项目时间线"""
        try:
            # 构建查询条件
            query = "type:project"
            if start_date:
                query += f" created_at:>={start_date.isoformat()}"
            if end_date:
                query += f" created_at:<={end_date.isoformat()}"

            # 搜索记忆
            memories = await self.storage.search_memories(query, limit)

            # 按时间排序
            memories.sort(key=lambda x: x.get("created_at", ""))

            return memories
            
        except Exception as e:
            logger.error(f"获取项目时间线失败: {e}")
            return []
    
    # ===== 个性化记忆管理 =====
    
    async def store_personal_memory(
        self,
        content: str,
        memory_type: str = "preference",
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> str:
        """存储个性化记忆"""
        try:
            personal_data = {
                "type": "personal",
                "content": content,
                "memory_type": memory_type,
                "metadata": metadata or {},
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "importance": metadata.get("importance", 1.0) if metadata else 1.0
            }
            
            memory_id = await self.storage.store_memory(personal_data)
            
            logger.info(f"个性化记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储个性化记忆失败: {e}")
            raise
    
    async def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        try:
            # 搜索个性化记忆
            preferences = await self.storage.search_memories(
                "type:personal memory_type:preference",
                limit=50
            )
            
            # 整理偏好信息
            user_preferences = {}
            for pref in preferences:
                pref_type = pref.get("metadata", {}).get("preference_type", "general")
                user_preferences[pref_type] = pref.get("content", "")
            
            return user_preferences
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return {}
    
    # ===== 记忆检索 =====
    
    async def retrieve_relevant_memories(
        self,
        query: str,
        memory_types: List[str] = None,
        limit: int = 10,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        try:
            # 使用记忆检索器
            relevant_memories = await self.memory_retriever.retrieve(
                query=query,
                memory_types=memory_types,
                limit=limit,
                threshold=threshold or RETRIEVAL_CONFIG.get("similarity_threshold", 0.5)
            )
            
            return relevant_memories
            
        except Exception as e:
            logger.error(f"检索相关记忆失败: {e}")
            return []
    
    async def build_context(self, query: str, context_limit: int = 5) -> Dict[str, Any]:
        """构建对话上下文"""
        try:
            # 检索相关记忆
            relevant_memories = await self.retrieve_relevant_memories(
                query=query,
                limit=context_limit
            )
            
            # 构建上下文
            context = {
                "relevant_memories": relevant_memories,
                "user_preferences": await self.get_user_preferences(),
                "recent_conversations": await self.get_conversation_history(limit=3),
                "project_status": await self.get_project_timeline(limit=5)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"构建上下文失败: {e}")
            return {"relevant_memories": []}
    
    # ===== 记忆管理 =====
    
    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新记忆"""
        try:
            success = await self.storage.update_memory(memory_id, updates)
            
            if success:
                logger.info(f"记忆已更新: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        try:
            success = await self.storage.delete_memory(memory_id)
            
            if success:
                logger.info(f"记忆已删除: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            # 更新统计信息
            stats = await self._calculate_memory_stats()
            self.memory_stats.update(stats)
            
            return self.memory_stats
            
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return self.memory_stats
    
    # ===== 批量操作 =====
    
    async def batch_store_memories(
        self,
        memories: List[Dict[str, Any]]
    ) -> List[str]:
        """批量存储记忆"""
        try:
            memory_ids = []
            
            for memory_data in memories:
                memory_id = await self.storage.store_memory(memory_data)
                memory_ids.append(memory_id)
            
            logger.info(f"批量存储了 {len(memory_ids)} 个记忆")
            return memory_ids
            
        except Exception as e:
            logger.error(f"批量存储记忆失败: {e}")
            raise
    
    async def batch_delete_memories(
        self,
        memory_ids: List[str]
    ) -> Dict[str, bool]:
        """批量删除记忆"""
        try:
            results = {}
            
            for memory_id in memory_ids:
                success = await self.delete_memory(memory_id)
                results[memory_id] = success
            
            logger.info(f"批量删除完成: {sum(results.values())}/{len(memory_ids)} 成功")
            return results
            
        except Exception as e:
            logger.error(f"批量删除记忆失败: {e}")
            raise
    
    # ===== 导入导出 =====
    
    async def export_memories(
        self,
        memory_types: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        export_format: str = "json"
    ) -> str:
        """导出记忆"""
        try:
            # 构建查询条件
            query = ""
            if memory_types:
                query += " OR ".join([f"type:{t}" for t in memory_types])
            
            if start_date or end_date:
                if query:
                    query += " "
                if start_date:
                    query += f"created_at:>={start_date.isoformat()} "
                if end_date:
                    query += f"created_at:<={end_date.isoformat()}"
            
            # 搜索记忆
            memories = await self.storage.search_memories(query, 1000)
            
            # 导出格式
            if export_format == "json":
                export_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_count": len(memories),
                    "memories": memories
                }
                return json.dumps(export_data, ensure_ascii=False, indent=2)
            
            elif export_format == "csv":
                # 简化的CSV格式
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入标题
                writer.writerow(["ID", "Type", "Content", "Tags", "Created At"])
                
                # 写入数据
                for memory in memories:
                    writer.writerow([
                        memory.get("id", ""),
                        memory.get("type", ""),
                        memory.get("content", "")[:100],  # 截断长内容
                        "|".join(memory.get("tags", [])),
                        memory.get("created_at", "")
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"不支持的导出格式: {export_format}")
                
        except Exception as e:
            logger.error(f"导出记忆失败: {e}")
            raise
    
    async def import_memories(
        self,
        import_data: str,
        import_format: str = "json"
    ) -> List[str]:
        """导入记忆"""
        try:
            if import_format == "json":
                data = json.loads(import_data)
                memories = data.get("memories", [])
            else:
                raise ValueError(f"不支持的导入格式: {import_format}")
            
            # 批量存储
            memory_ids = await self.batch_store_memories(memories)
            
            logger.info(f"导入完成: {len(memory_ids)} 个记忆")
            return memory_ids
            
        except Exception as e:
            logger.error(f"导入记忆失败: {e}")
            raise