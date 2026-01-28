from conversation_memory import ConversationMemory


def main():
    memory = ConversationMemory("my_conversations.json")
    
    print("=== 简单对话记忆示例 ===")
    
    memory.add_user_message("你好，我叫小明")
    memory.add_assistant_message("你好小明！很高兴认识你。")
    
    memory.add_user_message("我喜欢编程")
    memory.add_assistant_message("编程是个很棒的爱好！")
    
    memory.add_user_message("我在学习Python")
    memory.add_assistant_message("Python是一门很实用的编程语言。")
    
    print("\n当前会话对话:")
    for msg in memory.get_conversation():
        role = "小明" if msg['role'] == 'user' else "助手"
        print(f"{role}: {msg['content']}")
    
    print("\n最近2条消息:")
    for msg in memory.get_recent_messages(2):
        role = "小明" if msg['role'] == 'user' else "助手"
        print(f"{role}: {msg['content']}")
    
    print("\n搜索 'Python':")
    results = memory.search_conversations("Python")
    for result in results:
        role = "小明" if result['message']['role'] == 'user' else "助手"
        print(f"{role}: {result['message']['content']}")
    
    print("\n会话统计:")
    stats = memory.get_session_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()