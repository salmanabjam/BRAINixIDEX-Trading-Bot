"""
Performance Monitoring System
==============================
Monitor system metrics: CPU, RAM, API calls, latency.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import threading


class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self, history_size: int = 100):
        """Initialize monitor."""
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.ram_history = deque(maxlen=history_size)
        self.api_calls = deque(maxlen=history_size)
        self.latencies = deque(maxlen=history_size)
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram_usage(self) -> Dict[str, float]:
        """Get RAM usage info."""
        mem = psutil.virtual_memory()
        return {
            'total_gb': mem.total / (1024**3),
            'used_gb': mem.used / (1024**3),
            'available_gb': mem.available / (1024**3),
            'percent': mem.percent
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage info."""
        disk = psutil.disk_usage('/')
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent
        }
    
    def get_network_stats(self) -> Dict[str, int]:
        """Get network I/O stats."""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    def record_api_call(self, endpoint: str, duration: float):
        """Record an API call."""
        with self._lock:
            self.api_calls.append({
                'timestamp': datetime.now(),
                'endpoint': endpoint,
                'duration': duration
            })
            self.latencies.append(duration)
    
    def get_api_stats(self) -> Dict:
        """Get API call statistics."""
        with self._lock:
            if not self.api_calls:
                return {
                    'total_calls': 0,
                    'avg_latency': 0,
                    'min_latency': 0,
                    'max_latency': 0
                }
            
            latencies = list(self.latencies)
            return {
                'total_calls': len(self.api_calls),
                'avg_latency': sum(latencies) / len(latencies),
                'min_latency': min(latencies),
                'max_latency': max(latencies)
            }
    
    def update_history(self):
        """Update metrics history."""
        with self._lock:
            self.cpu_history.append({
                'timestamp': datetime.now(),
                'value': self.get_cpu_usage()
            })
            
            ram = self.get_ram_usage()
            self.ram_history.append({
                'timestamp': datetime.now(),
                'value': ram['percent']
            })
    
    def get_system_health(self) -> Dict:
        """Get overall system health status."""
        cpu = self.get_cpu_usage()
        ram = self.get_ram_usage()
        disk = self.get_disk_usage()
        
        # Determine health status
        if cpu > 80 or ram['percent'] > 80 or disk['percent'] > 90:
            status = 'critical'
        elif cpu > 60 or ram['percent'] > 60 or disk['percent'] > 75:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'cpu_percent': cpu,
            'ram_percent': ram['percent'],
            'disk_percent': disk['percent'],
            'uptime_seconds': time.time() - self.start_time
        }
    
    def get_metrics_summary(self) -> Dict:
        """Get complete metrics summary."""
        return {
            'cpu': self.get_cpu_usage(),
            'ram': self.get_ram_usage(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_stats(),
            'api_stats': self.get_api_stats(),
            'health': self.get_system_health()
        }


# Global instance
_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


if __name__ == "__main__":
    monitor = PerformanceMonitor()
    print("Performance Monitor Test")
    print(f"CPU: {monitor.get_cpu_usage()}%")
    print(f"RAM: {monitor.get_ram_usage()}")
    print(f"Health: {monitor.get_system_health()}")
