import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conversation_memory import ConversationMemory


class MemoryReviewDriver:
    def __init__(self, storage_path: str = "conversation_history.json", review_interval_minutes: int = 60):
        self.memory = ConversationMemory(storage_path)
        self.review_interval = review_interval_minutes
        self.last_review_time = None
        self.review_log_path = "memory_reviews.json"
        self._load_review_log()

    def _load_review_log(self):
        if os.path.exists(self.review_log_path):
            try:
                with open(self.review_log_path, 'r', encoding='utf-8') as f:
                    self.review_history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.review_history = []
        else:
            self.review_history = []

    def _save_review_log(self):
        with open(self.review_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.review_history, f, ensure_ascii=False, indent=2)

    def _summarize_conversation(self, messages: List[Dict]) -> str:
        if not messages:
            return "无对话内容"

        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]

        summary_parts = [
            f"总消息数: {len(messages)}",
            f"用户消息: {len(user_messages)}",
            f"助手消息: {len(assistant_messages)}"
        ]

        if messages:
            first_msg_time = messages[0].get("timestamp", "")
            last_msg_time = messages[-1].get("timestamp", "")
            if first_msg_time and last_msg_time:
                summary_parts.append(f"时间跨度: {first_msg_time[:10]} 至 {last_msg_time[:10]}")

        return "; ".join(summary_parts)

    def _extract_key_topics(self, messages: List[Dict]) -> List[str]:
        keywords = set()
        for msg in messages:
            content = msg.get("content", "").lower()
            words = content.split()
            keywords.update([word for word in words if len(word) > 3])
        return sorted(list(keywords))[:10]

    def review_session(self, session_id: str) -> Dict:
        messages = self.memory.get_conversation(session_id)
        
        if not messages:
            return {
                "session_id": session_id,
                "status": "empty",
                "summary": "该会话无内容"
            }

        review_result = {
            "session_id": session_id,
            "review_time": datetime.now().isoformat(),
            "status": "completed",
            "summary": self._summarize_conversation(messages),
            "message_count": len(messages),
            "key_topics": self._extract_key_topics(messages),
            "last_message": messages[-1].get("content", "")[:200] if messages else ""
        }

        return review_result

    def review_all_sessions(self) -> Dict:
        session_ids = self.memory.get_all_sessions()
        results = {
            "review_time": datetime.now().isoformat(),
            "total_sessions": len(session_ids),
            "sessions": []
        }

        for session_id in session_ids:
            result = self.review_session(session_id)
            results["sessions"].append(result)

        self.review_history.append(results)
        self._save_review_log()

        return results

    def review_recent_sessions(self, hours: int = 24) -> Dict:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        session_ids = self.memory.get_all_sessions()
        
        results = {
            "review_time": datetime.now().isoformat(),
            "review_period_hours": hours,
            "total_sessions": len(session_ids),
            "reviewed_sessions": [],
            "skipped_sessions": []
        }

        for session_id in session_ids:
            messages = self.memory.get_conversation(session_id)
            if messages:
                last_msg_time_str = messages[-1].get("timestamp", "")
                if last_msg_time_str:
                    last_msg_time = datetime.fromisoformat(last_msg_time_str)
                    if last_msg_time >= cutoff_time:
                        result = self.review_session(session_id)
                        results["reviewed_sessions"].append(result)
                    else:
                        results["skipped_sessions"].append(session_id)
                else:
                    results["reviewed_sessions"].append(self.review_session(session_id))
            else:
                results["skipped_sessions"].append(session_id)

        self.review_history.append(results)
        self._save_review_log()

        return results

    def print_review_summary(self, review_result: Dict):
        print("\n" + "="*60)
        print(f"记忆回顾报告 - {review_result['review_time']}")
        print("="*60)

        if "review_period_hours" in review_result:
            print(f"回顾时段: 最近 {review_result['review_period_hours']} 小时")

        print(f"总会话数: {review_result['total_sessions']}")

        if "reviewed_sessions" in review_result:
            print(f"已回顾: {len(review_result['reviewed_sessions'])}")
            print(f"跳过: {len(review_result['skipped_sessions'])}")

        print("\n详细结果:")
        print("-"*60)

        for session in review_result.get("sessions", review_result.get("reviewed_sessions", [])):
            print(f"\n会话ID: {session['session_id']}")
            print(f"状态: {session['status']}")
            if session['status'] == 'completed':
                print(f"摘要: {session['summary']}")
                print(f"消息数: {session['message_count']}")
                print(f"关键话题: {', '.join(session['key_topics'][:5])}")
                print(f"最后消息: {session['last_message'][:100]}...")

        print("\n" + "="*60)

    def start_auto_review(self, mode: str = "all", hours: Optional[int] = None):
        self.last_review_time = datetime.now()

        def job():
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动回顾...")

            if mode == "all":
                result = self.review_all_sessions()
            elif mode == "recent" and hours:
                result = self.review_recent_sessions(hours)
            else:
                result = self.review_all_sessions()

            self.print_review_summary(result)
            print(f"\n下一次回顾将在 {self.review_interval} 分钟后进行\n")
            self.last_review_time = datetime.now()

        print(f"\n自动回顾驱动已启动")
        print(f"回顾模式: {'全部会话' if mode == 'all' else f'最近 {hours} 小时'}")
        print(f"回顾间隔: {self.review_interval} 分钟")
        next_run = datetime.now() + timedelta(minutes=self.review_interval)
        print(f"下次回顾时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n按 Ctrl+C 停止\n")

        job()

        try:
            while True:
                time.sleep(self.review_interval * 60)
                job()
        except KeyboardInterrupt:
            print("\n自动回顾已停止")

    def trigger_one_time_review(self, mode: str = "all", hours: Optional[int] = None):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 触发一次性回顾...")

        if mode == "recent" and hours:
            result = self.review_recent_sessions(hours)
        else:
            result = self.review_all_sessions()

        self.print_review_summary(result)
        return result

    def get_review_stats(self) -> Dict:
        total_reviews = len(self.review_history)
        total_sessions_reviewed = sum(r.get("total_sessions", 0) for r in self.review_history)

        return {
            "total_reviews": total_reviews,
            "total_sessions_reviewed": total_sessions_reviewed,
            "last_review_time": self.review_history[-1]["review_time"] if self.review_history else None
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="记忆回顾驱动脚本")
    parser.add_argument("--mode", choices=["auto", "once"], default="once", help="运行模式: auto=自动定期回顾, once=一次性回顾")
    parser.add_argument("--interval", type=int, default=60, help="自动回顾间隔(分钟), 仅auto模式有效")
    parser.add_argument("--recent", type=int, help="只回顾最近N小时的对话")
    parser.add_argument("--stats", action="store_true", help="显示回顾统计信息")

    args = parser.parse_args()

    driver = MemoryReviewDriver(review_interval_minutes=args.interval)

    if args.stats:
        stats = driver.get_review_stats()
        print(f"回顾统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    elif args.mode == "auto":
        driver.start_auto_review(
            mode="recent" if args.recent else "all",
            hours=args.recent
        )
    else:
        driver.trigger_one_time_review(
            mode="recent" if args.recent else "all",
            hours=args.recent
        )
