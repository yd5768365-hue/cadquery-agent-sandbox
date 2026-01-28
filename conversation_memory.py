import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ConversationMemory:
    def __init__(self, storage_path: str = "conversation_history.json"):
        self.storage_path = storage_path
        self.conversations: Dict[str, List[Dict]] = {}
        self.current_session_id = self._generate_session_id()
        self._load_from_file()

    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _load_from_file(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.conversations = {}

    def _save_to_file(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, content: str, session_id: Optional[str] = None):
        session = session_id or self.current_session_id
        
        if session not in self.conversations:
            self.conversations[session] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[session].append(message)
        self._save_to_file()

    def add_user_message(self, content: str, session_id: Optional[str] = None):
        self.add_message("user", content, session_id)

    def add_assistant_message(self, content: str, session_id: Optional[str] = None):
        self.add_message("assistant", content, session_id)

    def get_conversation(self, session_id: Optional[str] = None) -> List[Dict]:
        session = session_id or self.current_session_id
        return self.conversations.get(session, [])

    def get_recent_messages(self, count: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        conversation = self.get_conversation(session_id)
        return conversation[-count:] if conversation else []

    def get_all_sessions(self) -> List[str]:
        return list(self.conversations.keys())

    def search_conversations(self, keyword: str, session_id: Optional[str] = None) -> List[Dict]:
        sessions_to_search = [session_id] if session_id else self.get_all_sessions()
        results = []
        
        for session in sessions_to_search:
            for message in self.conversations.get(session, []):
                if keyword.lower() in message.get("content", "").lower():
                    results.append({
                        "session_id": session,
                        "message": message
                    })
        
        return results

    def delete_session(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]
            self._save_to_file()

    def clear_current_session(self):
        if self.current_session_id in self.conversations:
            del self.conversations[self.current_session_id]
            self._save_to_file()
        self.current_session_id = self._generate_session_id()

    def export_session(self, session_id: str, export_path: str):
        conversation = self.get_conversation(session_id)
        if conversation:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)

    def get_session_stats(self, session_id: Optional[str] = None) -> Dict:
        session = session_id or self.current_session_id
        conversation = self.conversations.get(session, [])
        
        user_messages = sum(1 for msg in conversation if msg.get("role") == "user")
        assistant_messages = sum(1 for msg in conversation if msg.get("role") == "assistant")
        
        return {
            "session_id": session,
            "total_messages": len(conversation),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        }


if __name__ == "__main__":
    memory = ConversationMemory()
    
    print("对话记忆系统 - 交互式演示")
    print("输入 'quit' 退出，'history' 查看历史，'search <关键词>' 搜索")
    print("=" * 50)
    
    while True:
        user_input = input("\n你: ").strip()
        
        if user_input.lower() == 'quit':
            print("再见！")
            break
        
        if user_input.lower() == 'history':
            history = memory.get_conversation()
            print(f"\n当前会话历史 (共{len(history)}条消息):")
            for msg in history:
                role = "你" if msg['role'] == 'user' else "助手"
                print(f"{role}: {msg['content']}")
            continue
        
        if user_input.lower().startswith('search '):
            keyword = user_input[7:]
            results = memory.search_conversations(keyword)
            print(f"\n搜索结果 (共{len(results)}条):")
            for result in results:
                role = "你" if result['message']['role'] == 'user' else "助手"
                print(f"[{result['session_id']}] {role}: {result['message']['content']}")
            continue
        
        memory.add_user_message(user_input)
        
        response = f"我记住了你说: {user_input}"
        print(f"\n助手: {response}")
        memory.add_assistant_message(response)