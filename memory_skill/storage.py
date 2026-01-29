"""
存储抽象层
支持文件存储、数据库存储和外部API存储
"""

import json
import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from .config import MEMORY_CONFIG, EXTERNAL_API_CONFIG

logger = logging.getLogger(__name__)

class StorageInterface:
    """存储接口基类"""
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """存储记忆数据"""
        raise NotImplementedError
        
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """检索记忆数据"""
        raise NotImplementedError
        
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆"""
        raise NotImplementedError
        
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        raise NotImplementedError
        
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        raise NotImplementedError

class FileStorage(StorageInterface):
    """文件存储实现"""
    
    def __init__(self, storage_dir: str = "memory_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 创建不同类型的存储目录
        self.memory_types = ["conversation", "knowledge", "project", "personal"]
        for memory_type in self.memory_types:
            (self.storage_dir / memory_type).mkdir(exist_ok=True)
            
        # 创建索引文件
        self.index_file = self.storage_dir / "index.json"
        self._init_index()
        
    def _init_index(self):
        """初始化索引文件"""
        if not self.index_file.exists():
            index_data = {
                "memories": {},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _get_memory_path(self, memory_id: str, memory_type: str) -> Path:
        """获取记忆文件路径"""
        return self.storage_dir / memory_type / f"{memory_id}.json"
    
    def _load_index(self) -> Dict[str, Any]:
        """加载索引数据"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载索引失败: {e}")
            return {"memories": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_index(self, index_data: Dict[str, Any]):
        """保存索引数据"""
        try:
            index_data["last_updated"] = datetime.now().isoformat()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """存储记忆到文件"""
        memory_id = memory_data.get("id", self._generate_memory_id())
        memory_type = memory_data.get("type", "conversation")
        
        # 确保记忆数据包含必要字段
        memory_data["id"] = memory_id
        memory_data["created_at"] = memory_data.get("created_at", datetime.now().isoformat())
        memory_data["updated_at"] = datetime.now().isoformat()
        
        # 保存记忆文件
        memory_path = self._get_memory_path(memory_id, memory_type)
        try:
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            index_data = self._load_index()
            index_data["memories"][memory_id] = {
                "type": memory_type,
                "created_at": memory_data["created_at"],
                "file_path": str(memory_path),
                "tags": memory_data.get("tags", []),
                "summary": memory_data.get("summary", "")[:200]
            }
            self._save_index(index_data)
            
            logger.info(f"记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储记忆失败: {e}")
            raise
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """从文件检索记忆"""
        index_data = self._load_index()
        memory_info = index_data["memories"].get(memory_id)
        
        if not memory_info:
            return None
            
        try:
            memory_path = Path(memory_info["file_path"])
            if memory_path.exists():
                with open(memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"检索记忆失败: {e}")
            
        return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆（简单实现）"""
        index_data = self._load_index()
        results = []
        
        # 简单的文本匹配搜索
        query_lower = query.lower()
        for memory_id, memory_info in index_data["memories"].items():
            if len(results) >= limit:
                break
                
            # 检查标签和摘要
            if (query_lower in " ".join(memory_info.get("tags", [])).lower() or
                query_lower in memory_info.get("summary", "").lower()):
                
                memory_data = await self.retrieve_memory(memory_id)
                if memory_data:
                    results.append(memory_data)
        
        return results
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        memory_data = await self.retrieve_memory(memory_id)
        if not memory_data:
            return False
            
        # 更新数据
        memory_data.update(updates)
        memory_data["updated_at"] = datetime.now().isoformat()
        
        # 重新保存
        memory_type = memory_data["type"]
        memory_path = self._get_memory_path(memory_id, memory_type)
        
        try:
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            index_data = self._load_index()
            if memory_id in index_data["memories"]:
                index_data["memories"][memory_id].update({
                    "tags": memory_data.get("tags", []),
                    "summary": memory_data.get("summary", "")[:200]
                })
                self._save_index(index_data)
            
            logger.info(f"记忆已更新: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        index_data = self._load_index()
        memory_info = index_data["memories"].get(memory_id)
        
        if not memory_info:
            return False
            
        try:
            # 删除文件
            memory_path = Path(memory_info["file_path"])
            if memory_path.exists():
                memory_path.unlink()
            
            # 更新索引
            del index_data["memories"][memory_id]
            self._save_index(index_data)
            
            logger.info(f"记忆已删除: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False
    
    def _generate_memory_id(self) -> str:
        """生成记忆ID"""
        return f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

class DatabaseStorage(StorageInterface):
    """SQLite数据库存储实现"""
    
    def __init__(self, db_path: str = "memory_storage/memory.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建记忆表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance REAL DEFAULT 1.0
                )
            ''')
            
            # 创建记忆向量表（用于语义搜索）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_vectors (
                    memory_id TEXT PRIMARY KEY,
                    vector BLOB,
                    FOREIGN KEY (memory_id) REFERENCES memories (id)
                )
            ''')
            
            conn.commit()
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """存储记忆到数据库"""
        memory_id = memory_data.get("id", self._generate_memory_id())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO memories 
                (id, type, content, metadata, tags, created_at, updated_at, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory_id,
                memory_data.get("type", "conversation"),
                json.dumps(memory_data.get("content", ""), ensure_ascii=False),
                json.dumps(memory_data.get("metadata", {}), ensure_ascii=False),
                json.dumps(memory_data.get("tags", []), ensure_ascii=False),
                memory_data.get("created_at", datetime.now().isoformat()),
                datetime.now().isoformat(),
                memory_data.get("importance", 1.0)
            ))
            
            conn.commit()
        
        return memory_id
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """从数据库检索记忆"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "type": row[1],
                    "content": json.loads(row[2]),
                    "metadata": json.loads(row[3]),
                    "tags": json.loads(row[4]),
                    "created_at": row[5],
                    "updated_at": row[6],
                    "importance": row[7]
                }
        
        return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆（简单实现）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 简单的全文搜索
            cursor.execute('''
                SELECT * FROM memories 
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
            ''', (f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "type": row[1],
                    "content": json.loads(row[2]),
                    "metadata": json.loads(row[3]),
                    "tags": json.loads(row[4]),
                    "created_at": row[5],
                    "updated_at": row[6],
                    "importance": row[7]
                })
            
            return results
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新记忆"""
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ["type", "content", "metadata", "tags", "importance"]:
                set_clauses.append(f"{key} = ?")
                if key in ["content", "metadata", "tags"]:
                    values.append(json.dumps(value, ensure_ascii=False))
                else:
                    values.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(memory_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(f'''
                UPDATE memories 
                SET {", ".join(set_clauses)}
                WHERE id = ?
            ''', values)
            
            return cursor.rowcount > 0
    
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
            cursor.execute('DELETE FROM memory_vectors WHERE memory_id = ?', (memory_id,))
            
            return cursor.rowcount > 0
    
    def _generate_memory_id(self) -> str:
        """生成记忆ID"""
        return f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

class APIStorage(StorageInterface):
    """外部API存储实现"""
    
    def __init__(self, api_config: Dict[str, Any]):
        self.api_config = api_config
        self.enabled = api_config.get("enabled", False)
        
        if not self.enabled:
            logger.warning("API存储未启用")
            return
    
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """通过API存储记忆"""
        if not self.enabled:
            raise RuntimeError("API存储未启用")
        
        # 这里需要实现实际的API调用
        # 由于用户需要提供自己的API，这里只是一个框架
        logger.info("API存储功能需要用户配置自己的记忆模型API")
        
        # 临时返回一个ID
        memory_id = memory_data.get("id", self._generate_memory_id())
        return memory_id
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """通过API检索记忆"""
        if not self.enabled:
            raise RuntimeError("API存储未启用")
        
        logger.info("API检索功能需要用户配置自己的记忆模型API")
        return None
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """通过API搜索记忆"""
        if not self.enabled:
            raise RuntimeError("API存储未启用")
        
        logger.info("API搜索功能需要用户配置自己的记忆模型API")
        return []
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """通过API更新记忆"""
        if not self.enabled:
            raise RuntimeError("API存储未启用")
        
        logger.info("API更新功能需要用户配置自己的记忆模型API")
        return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """通过API删除记忆"""
        if not self.enabled:
            raise RuntimeError("API存储未启用")
        
        logger.info("API删除功能需要用户配置自己的记忆模型API")
        return False
    
    def _generate_memory_id(self) -> str:
        """生成记忆ID"""
        return f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

def get_storage(storage_type: str = "file", **kwargs) -> StorageInterface:
    """获取存储实例"""
    if storage_type == "file":
        return FileStorage(kwargs.get("storage_dir", "memory_storage"))
    elif storage_type == "database":
        return DatabaseStorage(kwargs.get("db_path", "memory_storage/memory.db"))
    elif storage_type == "api":
        return APIStorage(kwargs.get("api_config", EXTERNAL_API_CONFIG))
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")