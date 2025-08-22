from datetime import datetime
from collections import defaultdict
import json

class AgentMonitor:
    def __init__(self):
        self.tool_usage = defaultdict(int)
        self.query_types = defaultdict(int)
        self.response_times = []
        self.error_count = 0
        
    def log_tool_usage(self, tool_name: str):
        self.tool_usage[tool_name] += 1
        
    def log_query_type(self, query_type: str):
        self.query_types[query_type] += 1
        
    def log_response_time(self, duration: float):
        self.response_times.append({
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        })
        
    def log_error(self, error: str):
        self.error_count += 1
        
    def get_stats(self):
        return {
            "tool_usage": dict(self.tool_usage),
            "query_types": dict(self.query_types),
            "total_queries": sum(self.query_types.values()),
            "error_count": self.error_count,
            "avg_response_time": sum(r["duration"] for r in self.response_times) / len(self.response_times) if self.response_times else 0
        }

# Global monitor instance
agent_monitor = AgentMonitor()