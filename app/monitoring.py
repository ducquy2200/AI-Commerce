from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import asyncio

class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.endpoint_stats = defaultdict(int)
        self.response_times = []
        self.active_websockets = 0
        
    def record_request(self, endpoint: str, response_time: float):
        self.request_count += 1
        self.endpoint_stats[endpoint] += 1
        self.response_times.append(response_time)
        
                # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def record_error(self):
        self.error_count += 1
    
    def record_websocket_connection(self, connected: bool):
        if connected:
            self.active_websockets += 1
        else:
            self.active_websockets = max(0, self.active_websockets - 1)
    
    def get_metrics(self) -> Dict:
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "active_websockets": self.active_websockets,
            "average_response_time": round(avg_response_time, 3),
            "endpoint_statistics": dict(self.endpoint_stats),
            "timestamp": datetime.now().isoformat()
        }

# Global metrics instance
metrics = MetricsCollector()