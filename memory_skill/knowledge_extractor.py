"""
知识提取器模块
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """知识提取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 知识提取规则
        self.extraction_rules = {
            "definitions": {
                "patterns": [
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:是|指|定义为|表示为)\s*[^。！？\n]+[。！？])",
                    r"([A-Za-z\u4e00-\u9fa5]+(?:\s+[A-Za-z\u4e00-\u9fa5]+)*\s*[:：]\s*[^。！？\n]+[。！？])",
                    r"所谓([A-Za-z\u4e00-\u9fa5]+\s*[^，,、]+)，(?:是指|就是)\s*[^。！？\n]+[。！？]"
                ],
                "confidence_weight": 0.8
            },
            "formulas": {
                "patterns": [
                    r"([A-Za-z]+\s*=\s*[^。！？\n]+[。！？]?)",
                    r"([A-Za-z]+\s*\([^)]*\)\s*=\s*[^。！？\n]+[。！？]?)",
                    r"([A-Za-z]+\s*=\s*\d+(?:\.\d+)?\s*×?\s*[^。！？\n]+[。！？]?)"
                ],
                "confidence_weight": 0.9
            },
            "principles": {
                "patterns": [
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:原理|定理|定律|法则|公理)\s*[^。！？\n]+[。！？])",
                    r"根据([A-Za-z\u4e00-\u9fa5]+\s*(?:原理|定理|定律))[^。！？\n]+[。！？]",
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:原理|定理|定律))表明[^。！？\n]+[。！？]"
                ],
                "confidence_weight": 0.85
            },
            "methods": {
                "patterns": [
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:方法|步骤|流程|算法)\s*[^。！？\n]+[。！？])",
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:方法|步骤|流程))包括[^。！？\n]+[。！？]",
                    r"(使用|采用|应用)([A-Za-z\u4e00-\u9fa5]+\s*(?:方法|步骤|流程))[^。！？\n]+[。！？]"
                ],
                "confidence_weight": 0.75
            },
            "concepts": {
                "patterns": [
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:概念|思想|观点|理论)\s*[^。！？\n]+[。！？])",
                    r"([A-Za-z\u4e00-\u9fa5]+\s*(?:概念|思想|观点))是指[^。！？\n]+[。！？]"
                ],
                "confidence_weight": 0.7
            }
        }
        
        # CAE专业关键词
        self.cae_keywords = {
            "有限元": ["有限元", "FEM", "Finite Element", "单元", "节点", "网格"],
            "力学": ["应力", "应变", "位移", "力", "弯矩", "扭矩", "压力", "拉力"],
            "材料": ["弹性", "塑性", "刚度", "强度", "硬度", "韧性", "疲劳"],
            "分析": ["静力", "动力", "模态", "屈曲", "非线性", "线性", "接触"],
            "数学": ["矩阵", "向量", "微分", "积分", "方程", "求解", "收敛"],
            "软件": ["SolidWorks", "CalculiX", "Gmsh", "ANSYS", "ABAQUS", "Python"]
        }
        
        # 知识类型映射
        self.knowledge_types = {
            "definitions": "定义",
            "formulas": "公式",
            "principles": "原理",
            "methods": "方法",
            "concepts": "概念"
        }
    
    async def extract(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取知识"""
        knowledge_points = []
        
        try:
            # 预处理文本
            cleaned_text = self._preprocess_text(text)
            
            # 按类型提取知识
            for knowledge_type, rules in self.extraction_rules.items():
                type_knowledge = await self._extract_by_type(cleaned_text, knowledge_type, rules)
                knowledge_points.extend(type_knowledge)
            
            # 去重和过滤
            knowledge_points = self._deduplicate_knowledge(knowledge_points)
            knowledge_points = self._filter_knowledge(knowledge_points)
            
            # 丰富知识信息
            knowledge_points = await self._enrich_knowledge(knowledge_points, text)
            
            logger.info(f"从文本中提取了 {len(knowledge_points)} 个知识点")
            return knowledge_points
            
        except Exception as e:
            logger.error(f"知识提取失败: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 确保句子结尾有标点
        text = re.sub(r'([a-zA-Z0-9\u4e00-\u9fa5])(\s+|$)', r'\1。', text)
        
        return text.strip()
    
    async def _extract_by_type(self, text: str, knowledge_type: str, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """按类型提取知识"""
        knowledge_points = []
        
        for pattern in rules["patterns"]:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    if isinstance(match, tuple):
                        content = match[0] if match[0] else match[1] if len(match) > 1 else ""
                    else:
                        content = match
                    
                    if content and len(content.strip()) > 10:
                        knowledge_point = {
                            "content": content.strip(),
                            "type": self.knowledge_types.get(knowledge_type, knowledge_type),
                            "source_pattern": pattern,
                            "confidence": rules.get("confidence_weight", 0.7),
                            "extracted_at": datetime.now().isoformat()
                        }
                        
                        knowledge_points.append(knowledge_point)
                
            except Exception as e:
                logger.warning(f"模式匹配失败 {pattern}: {e}")
                continue
        
        return knowledge_points
    
    def _deduplicate_knowledge(self, knowledge_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重知识"""
        unique_points = []
        seen_contents = set()
        
        for point in knowledge_points:
            content = point.get("content", "").strip()
            content_key = re.sub(r'\s+', ' ', content.lower())
            
            if content_key not in seen_contents and len(content) > 10:
                seen_contents.add(content_key)
                unique_points.append(point)
        
        return unique_points
    
    def _filter_knowledge(self, knowledge_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤知识"""
        filtered_points = []
        
        for point in knowledge_points:
            content = point.get("content", "")
            
            # 过滤条件
            if (len(content) >= 10 and 
                len(content) <= 500 and 
                point.get("confidence", 0) >= 0.5):
                
                # 检查是否包含CAE相关内容
                if self._contains_cae_content(content):
                    filtered_points.append(point)
        
        return filtered_points
    
    def _contains_cae_content(self, text: str) -> bool:
        """检查是否包含CAE相关内容"""
        text_lower = text.lower()
        
        for category, keywords in self.cae_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return True
        
        return False
    
    async def _enrich_knowledge(self, knowledge_points: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """丰富知识信息"""
        enriched_points = []
        
        for point in knowledge_points:
            enriched_point = point.copy()
            
            # 提取关键词
            keywords = self._extract_keywords(point.get("content", ""))
            enriched_point["keywords"] = keywords
            
            # 分类领域
            domain = self._classify_domain(point.get("content", ""))
            enriched_point["domain"] = domain
            
            # 提取相关公式
            formulas = self._extract_formulas(point.get("content", ""))
            if formulas:
                enriched_point["formulas"] = formulas
            
            # 计算重要性
            importance = self._calculate_importance(point, original_text)
            enriched_point["importance"] = importance
            
            # 生成标签
            tags = self._generate_tags(point)
            enriched_point["tags"] = tags
            
            enriched_points.append(enriched_point)
        
        return enriched_points
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取长度大于2的单词和数字
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fa5]{3,}\b', text)
        return list(set(words))
    
    def _classify_domain(self, text: str) -> str:
        """分类知识领域"""
        text_lower = text.lower()
        
        domain_scores = {}
        
        for domain, keywords in self.cae_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            domain_scores[domain] = score
        
        # 返回得分最高的领域
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            return best_domain if domain_scores[best_domain] > 0 else "general"
        
        return "general"
    
    def _extract_formulas(self, text: str) -> List[str]:
        """提取公式"""
        formulas = re.findall(r'([A-Za-z]+\s*=\s*[^。！？\n]+)', text)
        return [f.strip() for f in formulas if len(f.strip()) > 5]
    
    def _calculate_importance(self, knowledge_point: Dict[str, Any], original_text: str) -> float:
        """计算知识重要性"""
        importance = knowledge_point.get("confidence", 0.5)
        
        # 根据知识类型调整
        type_weights = {
            "定义": 1.2,
            "公式": 1.5,
            "原理": 1.3,
            "方法": 1.1,
            "概念": 1.0
        }
        
        knowledge_type = knowledge_point.get("type", "")
        importance *= type_weights.get(knowledge_type, 1.0)
        
        # 根据内容长度调整
        content = knowledge_point.get("content", "")
        if 20 <= len(content) <= 200:
            importance *= 1.1
        
        # 根据关键词数量调整
        keywords = knowledge_point.get("keywords", [])
        if len(keywords) > 3:
            importance *= 1.2
        
        return min(max(importance, 0.1), 2.0)
    
    def _generate_tags(self, knowledge_point: Dict[str, Any]) -> List[str]:
        """生成标签"""
        tags = []
        
        # 添加类型标签
        knowledge_type = knowledge_point.get("type", "")
        if knowledge_type:
            tags.append(knowledge_type)
        
        # 添加领域标签
        domain = knowledge_point.get("domain", "")
        if domain and domain != "general":
            tags.append(domain)
        
        # 添加关键词标签
        keywords = knowledge_point.get("keywords", [])
        for keyword in keywords[:3]:  # 最多取前3个关键词
            tags.append(keyword)
        
        # 添加特殊标签
        content = knowledge_point.get("content", "").lower()
        if any(word in content for word in ["重要", "关键", "核心", "基础"]):
            tags.append("重要")
        
        if "公式" in content or "=" in content:
            tags.append("公式")
        
        return list(set(tags))
    
    async def extract_structured_knowledge(self, text: str) -> Dict[str, Any]:
        """提取结构化知识"""
        try:
            # 提取所有知识点
            knowledge_points = await self.extract(text)
            
            # 按类型分组
            structured_knowledge = {
                "definitions": [],
                "formulas": [],
                "principles": [],
                "methods": [],
                "concepts": [],
                "summary": {
                    "total_points": len(knowledge_points),
                    "domains": {},
                    "average_importance": 0.0
                }
            }
            
            total_importance = 0.0
            
            for point in knowledge_points:
                knowledge_type = point.get("type", "")
                content = point.get("content", "")
                
                # 添加到对应类型
                if knowledge_type in structured_knowledge:
                    structured_knowledge[knowledge_type].append({
                        "content": content,
                        "importance": point.get("importance", 1.0),
                        "tags": point.get("tags", []),
                        "domain": point.get("domain", "general")
                    })
                
                # 统计领域
                domain = point.get("domain", "general")
                if domain not in structured_knowledge["summary"]["domains"]:
                    structured_knowledge["summary"]["domains"][domain] = 0
                structured_knowledge["summary"]["domains"][domain] += 1
                
                total_importance += point.get("importance", 1.0)
            
            # 计算平均重要性
            if knowledge_points:
                structured_knowledge["summary"]["average_importance"] = total_importance / len(knowledge_points)
            
            return structured_knowledge
            
        except Exception as e:
            logger.error(f"提取结构化知识失败: {e}")
            return {"error": str(e)}
    
    async def validate_knowledge(self, knowledge_point: Dict[str, Any]) -> Dict[str, Any]:
        """验证知识质量"""
        validation_result = {
            "is_valid": True,
            "confidence": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        content = knowledge_point.get("content", "")
        
        # 检查内容长度
        if len(content) < 10:
            validation_result["is_valid"] = False
            validation_result["issues"].append("内容过短")
        
        if len(content) > 500:
            validation_result["suggestions"].append("建议精简内容")
        
        # 检查语言质量
        if not re.search(r'[。！？]$', content):
            validation_result["issues"].append("缺少结束标点")
        
        # 检查是否包含专业术语
        if not self._contains_cae_content(content):
            validation_result["suggestions"].append("建议增加CAE专业术语")
        
        # 计算置信度
        base_confidence = knowledge_point.get("confidence", 0.5)
        
        # 根据问题调整置信度
        if validation_result["issues"]:
            base_confidence *= 0.8
        
        validation_result["confidence"] = min(max(base_confidence, 0.1), 1.0)
        
        return validation_result