"""
记忆检索器模块
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from .storage import StorageInterface

logger = logging.getLogger(__name__)

class MemoryRetriever:
    """记忆检索器"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        
        # 检索配置
        self.retrieval_config = {
            "max_results": 10,
            "similarity_threshold": 0.5,
            "time_decay_factor": 0.95,
            "boost_recent": True,
            "boost_important": True,
            "fuzzy_match": True
        }
        
        # 词汇权重
        self.term_weights = {
            # CAE核心术语
            "有限元": 3.0, "FEM": 3.0, "应力": 2.5, "应变": 2.5,
            "位移": 2.0, "网格": 2.0, "节点": 2.0, "单元": 2.0,
            "材料": 2.0, "弹性": 2.0, "塑性": 2.0, "刚度": 2.0,
            "强度": 2.0, "分析": 1.5, "仿真": 1.5, "计算": 1.5,
            "求解": 1.5, "边界": 1.5, "载荷": 1.5, "约束": 1.5,
            
            # 动作词
            "如何": 1.2, "怎么": 1.2, "方法": 1.3, "步骤": 1.3,
            "原理": 1.4, "理论": 1.4, "定义": 1.3, "概念": 1.3,
            
            # 重要标记
            "重要": 2.0, "关键": 2.0, "核心": 2.0, "基础": 1.8,
            "注意": 1.5, "记住": 1.5, "必须": 1.5, "应该": 1.2
        }
    
    async def retrieve(
        self,
        query: str,
        memory_types: List[str] = None,
        limit: int = None,
        threshold: float = None,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        try:
            # 应用配置
            limit = limit or self.retrieval_config["max_results"]
            threshold = threshold or self.retrieval_config["similarity_threshold"]
            
            # 预处理查询
            processed_query = self._preprocess_query(query)
            
            # 构建搜索条件
            search_conditions = self._build_search_conditions(processed_query, memory_types)
            
            # 执行搜索
            candidate_memories = await self._search_memories(search_conditions, limit * 3)
            
            # 计算相似度
            scored_memories = await self._score_memories(candidate_memories, processed_query, context)
            
            # 过滤和排序
            filtered_memories = [
                mem for mem in scored_memories 
                if mem.get("similarity_score", 0) >= threshold
            ]
            
            # 按相似度排序
            filtered_memories.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            
            # 返回结果
            result = filtered_memories[:limit]
            
            logger.info(f"检索到 {len(result)} 个相关记忆 (查询: {query[:50]}...)")
            return result
            
        except Exception as e:
            logger.error(f"记忆检索失败: {e}")
            return []
    
    def _preprocess_query(self, query: str) -> Dict[str, Any]:
        """预处理查询"""
        processed = {
            "original": query,
            "lower": query.lower(),
            "tokens": self._tokenize(query),
            "keywords": self._extract_keywords(query),
            "entities": self._extract_entities(query)
        }
        
        return processed
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单实现：按空格和标点分词
        tokens = re.findall(r'\b[\w\u4e00-\u9fa5]+\b', text.lower())
        return tokens
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        tokens = self._tokenize(text)
        
        # 过滤停用词
        stop_words = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "个",
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
            "the", "is", "at", "which", "on", "and", "a", "to", "are", "as", "was", "were"
        }
        
        keywords = [token for token in tokens if token not in stop_words and len(token) > 1]
        return keywords
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体"""
        entities = []
        
        # 提取可能的实体（简单实现）
        # 专业术语
        technical_terms = [
            "有限元", "FEM", "应力", "应变", "位移", "网格", "节点", "单元",
            "材料", "弹性", "塑性", "刚度", "强度", "分析", "仿真", "计算",
            "SolidWorks", "CalculiX", "Gmsh", "ANSYS", "ABAQUS", "Python"
        ]
        
        for term in technical_terms:
            if term.lower() in text.lower():
                entities.append(term)
        
        return list(set(entities))
    
    def _build_search_conditions(self, processed_query: Dict[str, Any], memory_types: List[str] = None) -> Dict[str, Any]:
        """构建搜索条件"""
        conditions = {
            "query": processed_query["original"],
            "keywords": processed_query["keywords"],
            "entities": processed_query["entities"],
            "memory_types": memory_types or ["conversation", "knowledge", "project", "personal"]
        }
        
        return conditions
    
    async def _search_memories(self, conditions: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """搜索记忆"""
        all_memories = []
        
        # 构建搜索查询
        search_query = " ".join(conditions["keywords"])
        
        # 按记忆类型搜索
        for memory_type in conditions["memory_types"]:
            type_query = f"type:{memory_type} {search_query}"
            
            try:
                memories = await self.storage.search_memories(type_query, limit)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"搜索 {memory_type} 记忆失败: {e}")
        
        # 去重
        unique_memories = {}
        for memory in all_memories:
            memory_id = memory.get("id", "")
            if memory_id and memory_id not in unique_memories:
                unique_memories[memory_id] = memory
        
        return list(unique_memories.values())
    
    async def _score_memories(
        self, 
        memories: List[Dict[str, Any]], 
        processed_query: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """为记忆评分"""
        scored_memories = []
        
        for memory in memories:
            try:
                score = await self._calculate_similarity_score(memory, processed_query, context)
                
                # 添加评分信息
                memory_with_score = memory.copy()
                memory_with_score["similarity_score"] = score
                memory_with_score["score_details"] = self._get_score_details(memory, processed_query)
                
                scored_memories.append(memory_with_score)
                
            except Exception as e:
                logger.warning(f"评分记忆失败 {memory.get('id', 'unknown')}: {e}")
                continue
        
        return scored_memories
    
    async def _calculate_similarity_score(
        self, 
        memory: Dict[str, Any], 
        processed_query: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> float:
        """计算相似度分数"""
        base_score = 0.0
        
        # 获取记忆内容
        memory_content = self._get_memory_content(memory)
        if not memory_content:
            return 0.0
        
        # 1. 词汇匹配分数
        keyword_score = self._calculate_keyword_score(memory_content, processed_query)
        base_score += keyword_score * 0.4
        
        # 2. 实体匹配分数
        entity_score = self._calculate_entity_score(memory_content, processed_query)
        base_score += entity_score * 0.3
        
        # 3. 语义相似度（简单实现）
        semantic_score = self._calculate_semantic_score(memory_content, processed_query)
        base_score += semantic_score * 0.3
        
        # 4. 时间衰减
        if self.retrieval_config["boost_recent"]:
            time_score = self._calculate_time_score(memory)
            base_score *= time_score
        
        # 5. 重要性提升
        if self.retrieval_config["boost_important"]:
            importance_score = self._calculate_importance_score(memory)
            base_score *= importance_score
        
        # 6. 上下文提升
        if context:
            context_score = self._calculate_context_score(memory, context)
            base_score += context_score
        
        return min(max(base_score, 0.0), 1.0)
    
    def _get_memory_content(self, memory: Dict[str, Any]) -> str:
        """获取记忆内容"""
        content_parts = []
        
        # 根据记忆类型获取内容
        memory_type = memory.get("type", "")
        
        if memory_type == "conversation":
            content_parts.append(memory.get("user_input", ""))
            content_parts.append(memory.get("agent_response", ""))
        elif memory_type == "knowledge":
            content_parts.append(memory.get("content", ""))
        elif memory_type == "project":
            content_parts.append(memory.get("description", ""))
            details = memory.get("details", {})
            if isinstance(details, dict):
                content_parts.append(" ".join(str(v) for v in details.values()))
        elif memory_type == "personal":
            content_parts.append(memory.get("content", ""))
        
        # 添加标签
        tags = memory.get("tags", [])
        if tags:
            content_parts.extend(tags)
        
        return " ".join(filter(None, content_parts))
    
    def _calculate_keyword_score(self, memory_content: str, processed_query: Dict[str, Any]) -> float:
        """计算关键词匹配分数"""
        query_keywords = set(processed_query["keywords"])
        memory_keywords = set(self._extract_keywords(memory_content))
        
        if not query_keywords:
            return 0.0
        
        # 计算重叠度
        intersection = query_keywords.intersection(memory_keywords)
        
        if not intersection:
            return 0.0
        
        # 计算加权分数
        weighted_score = 0.0
        for keyword in intersection:
            weight = self.term_weights.get(keyword, 1.0)
            weighted_score += weight
        
        # 归一化
        max_possible = sum(self.term_weights.get(k, 1.0) for k in query_keywords)
        if max_possible > 0:
            return weighted_score / max_possible
        
        return len(intersection) / len(query_keywords)
    
    def _calculate_entity_score(self, memory_content: str, processed_query: Dict[str, Any]) -> float:
        """计算实体匹配分数"""
        query_entities = set(processed_query["entities"])
        memory_entities = set(self._extract_entities(memory_content))
        
        if not query_entities:
            return 0.0
        
        intersection = query_entities.intersection(memory_entities)
        
        if not intersection:
            return 0.0
        
        return len(intersection) / len(query_entities)
    
    def _calculate_semantic_score(self, memory_content: str, processed_query: Dict[str, Any]) -> float:
        """计算语义相似度（简单实现）"""
        # 使用词汇重叠作为语义相似度的简单近似
        query_tokens = set(processed_query["tokens"])
        memory_tokens = set(self._tokenize(memory_content))
        
        if not query_tokens or not memory_tokens:
            return 0.0
        
        # Jaccard相似度
        intersection = query_tokens.intersection(memory_tokens)
        union = query_tokens.union(memory_tokens)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_time_score(self, memory: Dict[str, Any]) -> float:
        """计算时间分数"""
        try:
            created_at = memory.get("created_at", "")
            if not created_at:
                return 1.0
            
            # 计算时间差
            create_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now()
            time_diff = (now - create_time).days
            
            # 时间衰减
            decay_factor = self.retrieval_config["time_decay_factor"]
            time_score = decay_factor ** min(time_diff / 30, 12)  # 最多衰减12个月
            
            return max(time_score, 0.1)
            
        except Exception as e:
            logger.warning(f"计算时间分数失败: {e}")
            return 1.0
    
    def _calculate_importance_score(self, memory: Dict[str, Any]) -> float:
        """计算重要性分数"""
        importance = memory.get("importance", 1.0)
        
        # 将重要性映射到乘数
        if importance >= 2.0:
            return 1.2
        elif importance >= 1.5:
            return 1.1
        elif importance >= 1.0:
            return 1.0
        else:
            return 0.9
    
    def _calculate_context_score(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """计算上下文分数"""
        context_score = 0.0
        
        # 检查会话ID匹配
        memory_session = memory.get("session_id", "")
        context_session = context.get("session_id", "")
        
        if memory_session and context_session and memory_session == context_session:
            context_score += 0.2
        
        # 检查用户ID匹配
        memory_user = memory.get("user_id", "")
        context_user = context.get("user_id", "")
        
        if memory_user and context_user and memory_user == context_user:
            context_score += 0.1
        
        # 检查主题匹配
        memory_topics = memory.get("topics", [])
        context_topics = context.get("topics", [])
        
        if memory_topics and context_topics:
            common_topics = set(memory_topics).intersection(set(context_topics))
            if common_topics:
                context_score += 0.1 * len(common_topics)
        
        return min(context_score, 0.5)
    
    def _get_score_details(self, memory: Dict[str, Any], processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """获取评分详情"""
        details = {
            "memory_id": memory.get("id", ""),
            "memory_type": memory.get("type", ""),
            "created_at": memory.get("created_at", ""),
            "importance": memory.get("importance", 1.0)
        }
        
        return details
    
    async def retrieve_by_context(
        self,
        context: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """根据上下文检索记忆"""
        try:
            # 构建上下文查询
            context_query = self._build_context_query(context)
            
            # 检索记忆
            memories = await self.retrieve(
                query=context_query,
                limit=limit,
                context=context
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"上下文检索失败: {e}")
            return []
    
    def _build_context_query(self, context: Dict[str, Any]) -> str:
        """构建上下文查询"""
        query_parts = []
        
        # 添加会话相关信息
        if "session_id" in context:
            query_parts.append(f"session:{context['session_id']}")
        
        # 添加用户相关信息
        if "user_id" in context:
            query_parts.append(f"user:{context['user_id']}")
        
        # 添加主题
        if "topics" in context:
            query_parts.extend(context["topics"])
        
        # 添加当前任务
        if "current_task" in context:
            query_parts.append(context["current_task"])
        
        return " ".join(query_parts)
    
    async def retrieve_similar_conversations(
        self,
        user_input: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """检索相似对话"""
        try:
            # 只检索对话类型的记忆
            memories = await self.retrieve(
                query=user_input,
                memory_types=["conversation"],
                limit=limit
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"相似对话检索失败: {e}")
            return []
    
    async def retrieve_relevant_knowledge(
        self,
        query: str,
        knowledge_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """检索相关知识"""
        try:
            # 构建查询条件
            search_query = query
            if knowledge_type:
                search_query += f" type:knowledge knowledge_type:{knowledge_type}"
            
            # 检索记忆
            memories = await self.retrieve(
                query=search_query,
                memory_types=["knowledge"],
                limit=limit
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"知识检索失败: {e}")
            return []