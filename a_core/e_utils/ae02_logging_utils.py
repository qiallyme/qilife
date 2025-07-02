import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import logging

class LoggingUtils:
    """Centralized logging utility for the Second Brain system"""
    
    def __init__(self, db_path: str = "./data/second_brain.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_log_table()
    
    def _ensure_log_table(self):
        """Ensure the activity_log table exists"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        activity_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        metadata TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception:
            # If database operations fail, we'll continue without logging
            pass
    
    def log_activity(self, activity_type: str, description: str, 
                    metadata: Optional[Dict[str, Any]] = None):
        """Log an activity to the database and console"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Console logging for immediate visibility
            print(f"[{timestamp}] {activity_type.upper()}: {description}")
            if metadata:
                print(f"  Metadata: {json.dumps(metadata, indent=2)}")
            
            # Database logging
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO activity_log (activity_type, description, metadata, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        activity_type,
                        description,
                        json.dumps(metadata) if metadata else None,
                        timestamp
                    ))
                    conn.commit()
                    
        except Exception as e:
            # Fallback to console only if database logging fails
            print(f"[{datetime.now().isoformat()}] LOGGING_ERROR: Failed to log activity: {str(e)}")
            print(f"  Original activity: {activity_type} - {description}")
    
    def log_error(self, error_type: str, error_message: str, 
                  context: Optional[Dict[str, Any]] = None):
        """Log an error with additional context"""
        metadata = {"error_type": error_type}
        if context:
            metadata.update(context)
        
        self.log_activity("error", error_message, metadata)
    
    def log_performance(self, operation: str, duration_seconds: float, 
                       additional_info: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        metadata = {
            "operation": operation,
            "duration_seconds": duration_seconds,
            "performance_level": self._get_performance_level(duration_seconds)
        }
        
        if additional_info:
            metadata.update(additional_info)
        
        self.log_activity(
            "performance",
            f"Operation '{operation}' completed in {duration_seconds:.2f} seconds",
            metadata
        )
    
    def _get_performance_level(self, duration: float) -> str:
        """Categorize performance based on duration"""
        if duration < 1.0:
            return "fast"
        elif duration < 5.0:
            return "normal"
        elif duration < 15.0:
            return "slow"
        else:
            return "very_slow"
    
    def log_file_operation(self, operation: str, file_path: str, 
                          status: str, additional_info: Optional[Dict[str, Any]] = None):
        """Log file operations specifically"""
        metadata = {
            "operation": operation,
            "file_path": file_path,
            "status": status
        }
        
        if additional_info:
            metadata.update(additional_info)
        
        self.log_activity(
            "file_operation",
            f"File {operation}: {Path(file_path).name} - {status}",
            metadata
        )
    
    def log_ai_operation(self, operation: str, model: str, 
                        tokens_used: Optional[int] = None, 
                        cost: Optional[float] = None,
                        additional_info: Optional[Dict[str, Any]] = None):
        """Log AI operations with usage metrics"""
        metadata = {
            "operation": operation,
            "model": model
        }
        
        if tokens_used:
            metadata["tokens_used"] = tokens_used
        if cost:
            metadata["estimated_cost"] = cost
        if additional_info:
            metadata.update(additional_info)
        
        description = f"AI {operation} using {model}"
        if tokens_used:
            description += f" ({tokens_used} tokens)"
        
        self.log_activity("ai_operation", description, metadata)
    
    def log_user_action(self, action: str, details: str, 
                       user_context: Optional[Dict[str, Any]] = None):
        """Log user actions and interactions"""
        metadata = {"action": action}
        if user_context:
            metadata.update(user_context)
        
        self.log_activity("user_action", f"User {action}: {details}", metadata)
    
    def get_recent_logs(self, hours: int = 24, 
                       activity_types: Optional[list] = None) -> list:
        """Retrieve recent log entries"""
        try:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            cutoff_iso = datetime.fromtimestamp(cutoff_time).isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                if activity_types:
                    placeholders = ','.join(['?' for _ in activity_types])
                    query = f"""
                        SELECT activity_type, description, metadata, timestamp
                        FROM activity_log
                        WHERE timestamp >= ? AND activity_type IN ({placeholders})
                        ORDER BY timestamp DESC
                    """
                    cursor.execute(query, [cutoff_iso] + activity_types)
                else:
                    cursor.execute("""
                        SELECT activity_type, description, metadata, timestamp
                        FROM activity_log
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                    """, (cutoff_iso,))
                
                rows = cursor.fetchall()
                logs = []
                
                for row in rows:
                    logs.append({
                        'activity_type': row[0],
                        'description': row[1],
                        'metadata': json.loads(row[2]) if row[2] else {},
                        'timestamp': row[3]
                    })
                
                return logs
                
        except Exception as e:
            self.log_error("log_retrieval_error", f"Failed to retrieve logs: {str(e)}")
            return []
    
    def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a summary of log activities"""
        try:
            logs = self.get_recent_logs(hours)
            
            summary = {
                'total_activities': len(logs),
                'activity_breakdown': {},
                'error_count': 0,
                'performance_issues': 0,
                'time_range_hours': hours
            }
            
            for log in logs:
                activity_type = log['activity_type']
                summary['activity_breakdown'][activity_type] = \
                    summary['activity_breakdown'].get(activity_type, 0) + 1
                
                if activity_type == 'error':
                    summary['error_count'] += 1
                elif activity_type == 'performance':
                    metadata = log.get('metadata', {})
                    if metadata.get('performance_level') in ['slow', 'very_slow']:
                        summary['performance_issues'] += 1
            
            return summary
            
        except Exception as e:
            return {
                'total_activities': 0,
                'activity_breakdown': {},
                'error_count': 1,
                'performance_issues': 0,
                'time_range_hours': hours,
                'summary_error': str(e)
            }
    
    def export_logs(self, format_type: str = 'json', 
                   hours: int = 24) -> Optional[str]:
        """Export logs in specified format"""
        try:
            logs = self.get_recent_logs(hours)
            
            if format_type.lower() == 'json':
                return json.dumps(logs, indent=2, default=str)
            elif format_type.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                if logs:
                    fieldnames = ['timestamp', 'activity_type', 'description', 'metadata']
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for log in logs:
                        writer.writerow({
                            'timestamp': log['timestamp'],
                            'activity_type': log['activity_type'],
                            'description': log['description'],
                            'metadata': json.dumps(log['metadata']) if log['metadata'] else ''
                        })
                
                return output.getvalue()
            else:
                return None
                
        except Exception as e:
            self.log_error("log_export_error", f"Failed to export logs: {str(e)}")
            return None
    
    def clear_old_logs(self, days_to_keep: int = 30):
        """Clear old log entries to manage database size"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            cutoff_iso = datetime.fromtimestamp(cutoff_time).isoformat()
            
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM activity_log
                        WHERE timestamp < ?
                    """, (cutoff_iso,))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    self.log_activity(
                        "maintenance",
                        f"Cleared {deleted_count} old log entries",
                        {"days_to_keep": days_to_keep, "deleted_count": deleted_count}
                    )
                    
        except Exception as e:
            self.log_error("log_cleanup_error", f"Failed to clear old logs: {str(e)}")
