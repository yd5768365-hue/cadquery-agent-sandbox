"""
对话记忆处理模块
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .storage import StorageInterface

logger = logging.getLogger(__name__)

class ConversationMemory:
    """对话记忆处理器"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.conversation_patterns = {
            # 问题模式
            "question": [
                r"^(什么是|怎么|如何|为什么|哪里|哪个|多少|几|是否|能不能|可不可以)",
                r"\?$",
                r"请解释",
                r"帮我理解",
                r"我想知道"
            ],
            # 指令模式
            "command": [
                r"^(帮我|请|创建|实现|编写|开发|设计|分析|计算|仿真)",
                r"^(运行|执行|测试|调试|优化|改进|修改|更新)"
            ],
            # 反馈模式
            "feedback": [
                r"^(谢谢|好的|明白了|清楚了|有道理|不错|很好|太棒了)",
                r"^(不对|错了|有问题|错误|不行|不可以|不能)"
            ],
            # 学习模式
            "learning": [
                r"^(学习|理解|掌握|研究|探讨|分析|总结|归纳)",
                r"(理论|原理|概念|定义|公式|定理|定律)"
            ]
        }
    
    async def process_conversation(
        self,
        user_input: str,
        agent_response: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """处理对话并提取结构化信息"""
        
        # 分析对话类型
        conversation_type = self._analyze_conversation_type(user_input)
        
        # 提取关键信息
        key_info = self._extract_key_information(user_input, agent_response)
        
        # 生成对话摘要
        summary = self._generate_conversation_summary(user_input, agent_response)
        
        # 识别主题
        topics = self._identify_topics(user_input, agent_response)
        
        # 评估重要性
        importance = self._evaluate_importance(user_input, agent_response, conversation_type)
        
        # 构建对话记忆数据
        conversation_data = {
            "type": "conversation",
            "conversation_type": conversation_type,
            "user_input": user_input,
            "agent_response": agent_response,
            "summary": summary,
            "key_information": key_info,
            "topics": topics,
            "importance": importance,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "session_id": context.get("session_id", "") if context else "",
            "user_id": context.get("user_id", "default") if context else "default"
        }
        
        return conversation_data
    
    def _analyze_conversation_type(self, user_input: str) -> str:
        """分析对话类型"""
        user_input = user_input.lower().strip()
        
        for conv_type, patterns in self.conversation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return conv_type
        
        return "general"
    
    def _extract_key_information(self, user_input: str, agent_response: str) -> Dict[str, Any]:
        """提取关键信息"""
        key_info = {
            "questions": [],
            "answers": [],
            "commands": [],
            "concepts": [],
            "formulas": [],
            "references": []
        }
        
        # 提取问题
        questions = re.findall(r'([^。！？\n]*[？?])', user_input)
        key_info["questions"] = [q.strip() for q in questions if q.strip()]
        
        # 提取概念（简单实现）
        concepts = re.findall(r'([A-Za-z0-9_]+(?:\s+[A-Za-z0-9_]+)*)', user_input)
        key_info["concepts"] = list(set([c.strip() for c in concepts if len(c.strip()) > 2]))
        
        # 提取公式（简单实现）
        formulas = re.findall(r'([A-Za-z]+\s*=\s*[^。！？\n]+)', user_input + " " + agent_response)
        key_info["formulas"] = [f.strip() for f in formulas]
        
        # 提取引用（简单实现）
        references = re.findall(r'([第]+\s*[一二三四五六七八九十\d]+\s*[章节部分页])', user_input + " " + agent_response)
        key_info["references"] = references
        
        return key_info
    
    def _generate_conversation_summary(self, user_input: str, agent_response: str) -> str:
        """生成对话摘要"""
        # 简单实现：取用户输入的前30个字符和回复的前50个字符
        user_summary = user_input[:30] + "..." if len(user_input) > 30 else user_input
        response_summary = agent_response[:50] + "..." if len(agent_response) > 50 else agent_response
        
        return f"用户: {user_summary} | 回复: {response_summary}"
    
    def _identify_topics(self, user_input: str, agent_response: str) -> List[str]:
        """识别对话主题"""
        # CAE相关主题关键词
        cae_topics = [
            "有限元", "FEM", "CAE", "仿真", "分析", "应力", "应变", "位移",
            "网格", "划分", "求解", "计算", "材料", "力学", "弹性", "塑性",
            "接触", "边界", "载荷", "约束", "收敛", "误差", "验证", "对比",
            "SolidWorks", "CalculiX", "Gmsh", "Python", "代码", "算法",
            "理论", "公式", "模型", "几何", "装配", "零件", "工程", "项目"
        ]
        
        # 查找主题
        full_text = (user_input + " " + agent_response).lower()
        found_topics = []
        
        for topic in cae_topics:
            if topic.lower() in full_text:
                found_topics.append(topic)
        
        return list(set(found_topics))
    
    def _evaluate_importance(self, user_input: str, agent_response: str, conversation_type: str) -> float:
        """评估对话重要性"""
        importance = 1.0  # 基础重要性
        
        # 根据对话类型调整重要性
        type_weights = {
            "question": 1.2,
            "command": 1.3,
            "feedback": 0.8,
            "learning": 1.5,
            "general": 1.0
        }
        
        importance *= type_weights.get(conversation_type, 1.0)
        
        # 根据内容长度调整
        total_length = len(user_input) + len(agent_response)
        if total_length > 500:
            importance *= 1.2
        
        # 根据关键词调整
        important_keywords = [
            "重要", "关键", "核心", "基础", "原理", "理论", "公式", "定理",
            "注意", "记住", "必须", "应该", "推荐", "最佳实践"
        ]
        
        full_text = (user_input + " " + agent_response).lower()
        keyword_count = sum(1 for keyword in important_keywords if keyword in full_text)
        
        if keyword_count > 0:
            importance *= (1 + 0.1 * keyword_count)
        
        # 限制重要性范围
        return min(max(importance, 0.5), 3.0)
    
    async def get_conversation_context(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取会话上下文"""
        try:
            # 搜索相关对话记忆
            query = f"type:conversation session_id:{session_id}"
            memories = await self.storage.search_memories(query, limit * 2)
            
            # 按时间排序
            memories.sort(key=lambda x: x.get("timestamp", ""))
            
            # 返回最近的对话
            return memories[-limit:] if memories else []
            
        except Exception as e:
            logger.error(f"获取对话上下文失败: {e}")
            return []
    
    async def find_similar_conversations(
        self,
        user_input: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """查找相似对话"""
        try:
            # 提取关键词
            keywords = self._extract_keywords(user_input)
            
            if not keywords:
                return []
            
            # 构建搜索查询
            query = "type:conversation " + " OR ".join(keywords)
            
            # 搜索记忆
            memories = await self.storage.search_memories(query, limit * 3)
            
            # 计算相似度并排序
            similar_memories = []
            for memory in memories:
                similarity = self._calculate_similarity(user_input, memory.get("user_input", ""))
                if similarity > 0.3:  # 相似度阈值
                    memory["similarity"] = similarity
                    similar_memories.append(memory)
            
            # 按相似度排序
            similar_memories.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            return similar_memories[:limit]
            
        except Exception as e:
            logger.error(f"查找相似对话失败: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取长度大于2的单词
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fa5]{3,}\b', text)
        return list(set(words))
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        # 将文本转换为小写并分词
        words1 = set(self._extract_keywords(text1.lower()))
        words2 = set(self._extract_keywords(text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def analyze_conversation_patterns(
        self,
        session_id: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """分析对话模式"""
        try:
            # 构建时间范围
            end_date = datetime.now()
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 搜索对话记忆
            query = "type:conversation"
            if session_id:
                query += f" session_id:{session_id}"
            
            memories = await self.storage.search_memories(query, 1000)
            
            # 过滤时间范围内的记忆
            filtered_memories = []
            for memory in memories:
                try:
                    memory_date = datetime.fromisoformat(memory.get("timestamp", ""))
                    if (end_date - memory_date).days <= days:
                        filtered_memories.append(memory)
                except:
                    continue
            
            # 分析模式
            patterns = {
                "total_conversations": len(filtered_memories),
                "conversation_types": {},
                "topic_distribution": {},
                "average_importance": 0.0,
                "time_distribution": {}
            }
            
            total_importance = 0.0
            
            for memory in filtered_memories:
                # 对话类型统计
                conv_type = memory.get("conversation_type", "general")
                patterns["conversation_types"][conv_type] = patterns["conversation_types"].get(conv_type, 0) + 1
                
                # 主题分布
                topics = memory.get("topics", [])
                for topic in topics:
                    patterns["topic_distribution"][topic] = patterns["topic_distribution"].get(topic, 0) + 1
                
                # 重要性统计
                importance = memory.get("importance", 1.0)
                total_importance += importance
                
                # 时间分布
                try:
                    hour = datetime.fromisoformat(memory.get("timestamp", "")).hour
                    time_slot = f"{hour:02d}:00"
                    patterns["time_distribution"][time_slot] = patterns["time_distribution"].get(time_slot, 0) + 1
                except:
                    continue
            
            # 计算平均重要性
            if filtered_memories:
                patterns["average_importance"] = total_importance / len(filtered_memories)
            
            return patterns
            
        except Exception as e:
            logger.error(f"分析对话模式失败: {e}")
            return {}
    
    async def generate_conversation_report(
        self,
        session_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> str:
        """生成对话报告"""
        try:
            # 获取对话模式分析
            patterns = await self.analyze_conversation_patterns(session_id)
            
            # 生成报告
            report = f"""
# 对话分析报告

## 基本信息
- 对话总数: {patterns.get('total_conversations', 0)}
- 平均重要性: {patterns.get('average_importance', 0.0):.2f}

## 对话类型分布
"""
            
            for conv_type, count in patterns.get("conversation_types", {}).items():
                report += f"- {conv_type}: {count}\n"
            
            report += "\n## 热门主题\n"
            
            # 按频率排序主题
            sorted_topics = sorted(patterns.get("topic_distribution", {}).items(), 
                                 key=lambda x: x[1], reverse=True)
            
            for topic, count in sorted_topics[:10]:  # 显示前10个主题
                report += f"- {topic}: {count}\n"
            
            report += "\n## 时间分布\n"
            
            # 按时间排序
            sorted_times = sorted(patterns.get("time_distribution", {}).items())
            
            for time_slot, count in sorted_times:
                report += f"- {time_slot}: {count}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"生成对话报告失败: {e}")
            return f"生成报告时出错: {e}"