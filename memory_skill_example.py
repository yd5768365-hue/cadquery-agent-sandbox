#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统使用示例
演示如何在CAE智能体中集成记忆功能
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加记忆技能路径
import sys
sys.path.append(str(Path(__file__).parent / "memory_skill"))

from memory_skill.memory_manager import MemoryManager
from memory_skill.config import MEMORY_CONFIG, EXTERNAL_API_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def basic_memory_example():
    """基础记忆功能示例"""
    print("=== 基础记忆功能示例 ===")
    
    # 初始化记忆管理器
    memory_manager = MemoryManager()
    
    # 记录对话
    conversation_id = await memory_manager.remember_conversation(
        user_input="什么是应力集中系数？",
        agent_response="应力集中系数(Kt)是指在应力集中区域的最大应力与名义应力的比值。对于圆孔，理论值约为3。",
        tags=["应力集中", "系数", "理论"],
        importance=1.5
    )
    
    print(f"对话记忆ID: {conversation_id}")
    
    # 存储知识
    knowledge_id = await memory_manager.store_knowledge(
        content="应力集中系数(Kt) = σ_max / σ_nom，其中σ_max为最大应力，σ_nom为名义应力。",
        knowledge_type="公式",
        tags=["应力集中", "系数", "公式"],
        source=f"conversation:{conversation_id}"
    )
    
    print(f"知识记忆ID: {knowledge_id}")
    
    # 记录项目事件
    project_id = await memory_manager.store_project_memory(
        event_type="learning",
        description="学习了应力集中理论，理解了Kt的计算方法",
        details={
            "topic": "应力集中",
            "progress": "basic",
            "next_step": "实践验证"
        },
        tags=["学习", "应力集中", "理论"]
    )
    
    print(f"项目记忆ID: {project_id}")
    
    # 存储用户偏好
    preference_id = await memory_manager.store_personal_memory(
        content="用户偏好详细的数学推导和理论解释",
        memory_type="preference",
        metadata={
            "preference_type": "learning_style",
            "importance": 1.2
        },
        tags=["偏好", "学习风格", "理论"]
    )
    
    print(f"个性化记忆ID: {preference_id}")
    
    return memory_manager

async def context_building_example(memory_manager):
    """上下文构建示例"""
    print("\n=== 上下文构建示例 ===")
    
    # 构建对话上下文
    context = await memory_manager.build_context(
        query="如何计算应力集中系数？",
        context_limit=3
    )
    
    print(f"上下文包含 {len(context.get('relevant_memories', []))} 个相关记忆")
    print(f"用户偏好: {len(context.get('user_preferences', {}))} 项")
    print(f"最近对话: {len(context.get('recent_conversations', []))} 条")
    print(f"项目事件: {len(context.get('project_status', []))} 条")
    
    # 显示相关记忆
    print("\n相关记忆:")
    for i, memory in enumerate(context.get('relevant_memories', [])[:2], 1):
        print(f"{i}. {memory.get('type', 'unknown')} - {memory.get('content', '')[:50]}...")
    
    return context

async def knowledge_retrieval_example(memory_manager):
    """知识检索示例"""
    print("\n=== 知识检索示例 ===")
    
    # 搜索相关知识
    knowledge_memories = await memory_manager.search_knowledge(
        query="应力集中系数",
        limit=5
    )
    
    print(f"找到 {len(knowledge_memories)} 条相关知识:")
    for i, knowledge in enumerate(knowledge_memories, 1):
        print(f"{i}. {knowledge.get('knowledge_type', 'unknown')}: {knowledge.get('content', '')[:60]}...")
    
    return knowledge_memories

async def conversation_analysis_example(memory_manager):
    """对话分析示例"""
    print("\n=== 对话分析示例 ===")
    
    # 模拟多轮对话
    conversations = [
        {
            "user_input": "什么是有限元分析？",
            "agent_response": "有限元分析(FEA)是一种数值计算方法，用于求解工程中的偏微分方程。"
        },
        {
            "user_input": "网格划分有什么重要性？",
            "agent_response": "网格划分直接影响计算精度和效率，需要根据分析需求选择合适的网格密度。"
        },
        {
            "user_input": "如何验证仿真结果的准确性？",
            "agent_response": "可以通过理论计算、实验验证或与已知结果对比来验证仿真结果的准确性。"
        }
    ]
    
    # 记录对话
    for conv in conversations:
        await memory_manager.remember_conversation(
            user_input=conv["user_input"],
            agent_response=conv["agent_response"],
            tags=["有限元", "学习"],
            importance=1.2
        )
    
    # 分析对话模式
    from memory_skill.conversation_memory import ConversationMemory
    
    conversation_memory = ConversationMemory(memory_manager.storage)
    patterns = await conversation_memory.analyze_conversation_patterns()
    
    print("对话模式分析:")
    print(f"- 总对话数: {patterns.get('total_conversations', 0)}")
    print(f"- 对话类型: {patterns.get('conversation_types', {})}")
    print(f"- 热门主题: {list(patterns.get('topic_distribution', {}).keys())[:5]}")
    
    return patterns

async def knowledge_extraction_example(memory_manager):
    """知识提取示例"""
    print("\n=== 知识提取示例 ===")
    
    # 示例文本
    sample_text = """
    有限元分析的基本原理是将连续的结构离散为有限个简单单元的集合。
    每个单元通过节点相互连接，形成整体的离散模型。
    根据虚功原理，可以建立单元刚度矩阵，然后组装成总体刚度矩阵。
    基本方程为：[K]{u} = {F}，其中[K]是刚度矩阵，{u}是位移向量，{F}是载荷向量。
    这个方法可以处理复杂的几何形状和边界条件。
    """
    
    # 提取知识
    from memory_skill.knowledge_extractor import KnowledgeExtractor
    
    extractor = KnowledgeExtractor()
    knowledge_points = await extractor.extract(sample_text)
    
    print(f"从文本中提取了 {len(knowledge_points)} 个知识点:")
    for i, point in enumerate(knowledge_points, 1):
        print(f"{i}. {point.get('type', 'unknown')}: {point.get('content', '')[:80]}...")
        print(f"   标签: {point.get('tags', [])}")
        print(f"   重要性: {point.get('importance', 1.0):.2f}")
    
    # 存储提取的知识
    for point in knowledge_points:
        await memory_manager.store_knowledge(
            content=point["content"],
            knowledge_type=point["type"],
            metadata={
                "confidence": point.get("confidence", 1.0),
                "importance": point.get("importance", 1.0)
            },
            tags=point.get("tags", []),
            source="knowledge_extraction"
        )
    
    return knowledge_points

async def memory_statistics_example(memory_manager):
    """记忆统计示例"""
    print("\n=== 记忆统计示例 ===")
    
    # 获取记忆统计
    stats = await memory_manager.get_memory_stats()
    
    print("记忆统计信息:")
    print(f"- 总记忆数: {stats.get('total_memories', 0)}")
    print(f"- 按类型分布: {stats.get('by_type', {})}")
    print(f"- 最后清理时间: {stats.get('last_cleanup', 'N/A')}")
    
    return stats

async def export_import_example(memory_manager):
    """导入导出示例"""
    print("\n=== 导入导出示例 ===")
    
    # 导出记忆
    export_data = await memory_manager.export_memories(
        memory_types=["knowledge", "conversation"],
        export_format="json"
    )
    
    print(f"导出数据长度: {len(export_data)} 字符")
    
    # 保存到文件
    export_file = Path("memory_export.json")
    with open(export_file, 'w', encoding='utf-8') as f:
        f.write(export_data)
    
    print(f"导出文件: {export_file.absolute()}")
    
    # 导入记忆（示例）
    try:
        imported_ids = await memory_manager.import_memories(export_data)
        print(f"导入记忆数: {len(imported_ids)}")
    except Exception as e:
        print(f"导入失败: {e}")
    
    return export_data

async def api_integration_example():
    """API集成示例"""
    print("\n=== API集成示例 ===")
    
    # 配置外部API（这里只是示例，实际使用时需要提供真实的API配置）
    api_config = EXTERNAL_API_CONFIG.copy()
    api_config.update({
        "enabled": False,  # 设置为True以启用外部API
        "endpoint": "https://your-memory-api.com",
        "api_key": "your-api-key-here"
    })
    
    if api_config["enabled"]:
        from memory_skill.api_integration import ExternalMemoryAPI
        
        async with ExternalMemoryAPI(api_config) as api:
            # 测试连接
            health_check = await api.test_connection()
            print(f"API连接状态: {health_check}")
            
            # 如果连接成功，可以执行API操作
            if health_check.get("status") == "success":
                # 存储记忆到外部API
                memory_data = {
                    "type": "conversation",
                    "content": "通过API存储的记忆",
                    "tags": ["API", "外部存储"]
                }
                
                result = await api.store_memory(memory_data)
                print(f"API存储结果: {result}")
    else:
        print("外部API未启用 - 跳过API集成示例")
        print("要启用API集成，请在config.py中设置EXTERNAL_API_CONFIG['enabled'] = True")

async def main():
    """主函数"""
    print("CAE智能体记忆系统使用示例")
    print("=" * 50)
    
    try:
        # 基础记忆功能
        memory_manager = await basic_memory_example()
        
        # 上下文构建
        await context_building_example(memory_manager)
        
        # 知识检索
        await knowledge_retrieval_example(memory_manager)
        
        # 对话分析
        await conversation_analysis_example(memory_manager)
        
        # 知识提取
        await knowledge_extraction_example(memory_manager)
        
        # 记忆统计
        await memory_statistics_example(memory_manager)
        
        # 导入导出
        await export_import_example(memory_manager)
        
        # API集成
        await api_integration_example()
        
        print("\n" + "=" * 50)
        print("所有示例执行完成！")
        
        # 显示最终统计
        final_stats = await memory_manager.get_memory_stats()
        print(f"\n最终记忆统计:")
        print(f"- 总记忆数: {final_stats.get('total_memories', 0)}")
        print(f"- 记忆类型分布: {final_stats.get('by_type', {})}")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())