import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading
from a_core.e_utils.ae02_logging_utils import LoggingUtils

class DatabaseManager:
    """Manage SQLite database for file analysis and metadata"""
    
    def __init__(self, db_path: str = "./data/second_brain.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.logger = LoggingUtils()
        self._lock = threading.Lock()
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Files analysis table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS file_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE NOT NULL,
                        original_name TEXT NOT NULL,
                        suggested_name TEXT NOT NULL,
                        content TEXT,
                        metadata TEXT,
                        entities TEXT,
                        confidence REAL,
                        reasoning TEXT,
                        vector_id TEXT,
                        event_type TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Entities table for consistency tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_name TEXT UNIQUE NOT NULL,
                        variations TEXT,
                        usage_count INTEGER DEFAULT 1,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Document context for memory
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS document_context (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        entities TEXT,
                        content_summary TEXT,
                        keywords TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Activity log
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        activity_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        metadata TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # File processing history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        file_hash TEXT,
                        last_processed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON file_analysis(file_path)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities ON file_analysis(entities)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON file_analysis(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON file_analysis(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_type ON activity_log(activity_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON activity_log(timestamp)")
                
                conn.commit()
                
            self.logger.log_activity(
                "database_initialized",
                "Database initialized successfully",
                {"db_path": str(self.db_path)}
            )
            
        except Exception as e:
            self.logger.log_activity(
                "database_init_error",
                f"Error initializing database: {str(e)}",
                {"error": str(e), "db_path": str(self.db_path)}
            )
            raise
    
    def store_file_analysis(self, file_path: str, original_name: str, suggested_name: str,
                          content: str, metadata: Dict[str, Any], entities: List[str],
                          confidence: float, reasoning: str, vector_id: str, event_type: str):
        """Store file analysis results"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO file_analysis
                        (file_path, original_name, suggested_name, content, metadata, entities,
                         confidence, reasoning, vector_id, event_type, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_path, original_name, suggested_name, content,
                        json.dumps(metadata), json.dumps(entities),
                        confidence, reasoning, vector_id, event_type,
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                    
            # Update entity usage
            for entity in entities:
                self._update_entity_usage(entity)
                
        except Exception as e:
            self.logger.log_activity(
                "file_analysis_storage_error",
                f"Error storing file analysis: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
            raise
    
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get all files pending review"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, file_path, original_name, suggested_name, entities,
                           confidence, reasoning, created_at
                    FROM file_analysis
                    WHERE status = 'pending'
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'id': row[0],
                        'file_path': row[1],
                        'original_name': row[2],
                        'suggested_name': row[3],
                        'entities': json.loads(row[4]) if row[4] else [],
                        'confidence': row[5],
                        'reasoning': row[6],
                        'created_at': row[7]
                    })
                
                return results
                
        except Exception as e:
            self.logger.log_activity(
                "pending_reviews_error",
                f"Error getting pending reviews: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def approve_file_rename(self, file_id: int, approved_name: str = None):
        """Approve a file rename suggestion"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    if approved_name:
                        cursor.execute("""
                            UPDATE file_analysis
                            SET status = 'approved', suggested_name = ?, updated_at = ?
                            WHERE id = ?
                        """, (approved_name, datetime.now().isoformat(), file_id))
                    else:
                        cursor.execute("""
                            UPDATE file_analysis
                            SET status = 'approved', updated_at = ?
                            WHERE id = ?
                        """, (datetime.now().isoformat(), file_id))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.log_activity(
                "approve_rename_error",
                f"Error approving file rename: {str(e)}",
                {"file_id": file_id, "error": str(e)}
            )
            raise
    
    def reject_file_rename(self, file_id: int):
        """Reject a file rename suggestion"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE file_analysis
                        SET status = 'rejected', updated_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), file_id))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.log_activity(
                "reject_rename_error",
                f"Error rejecting file rename: {str(e)}",
                {"file_id": file_id, "error": str(e)}
            )
            raise
    
    def store_entity(self, entity_name: str, variations: List[str]):
        """Store a new entity"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO entities
                        (entity_name, variations, usage_count, last_seen)
                        VALUES (?, ?, ?, ?)
                    """, (entity_name, json.dumps(variations), 1, datetime.now().isoformat()))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.log_activity(
                "entity_storage_error",
                f"Error storing entity: {str(e)}",
                {"entity_name": entity_name, "error": str(e)}
            )
            raise
    
    def _update_entity_usage(self, entity_name: str):
        """Update entity usage count"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE entities
                    SET usage_count = usage_count + 1, last_seen = ?
                    WHERE entity_name = ?
                """, (datetime.now().isoformat(), entity_name))
                
                if cursor.rowcount == 0:
                    # Entity doesn't exist, create it
                    cursor.execute("""
                        INSERT INTO entities (entity_name, variations, usage_count, last_seen)
                        VALUES (?, ?, 1, ?)
                    """, (entity_name, json.dumps([]), datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.log_activity(
                "entity_usage_update_error",
                f"Error updating entity usage: {str(e)}",
                {"entity_name": entity_name, "error": str(e)}
            )
    
    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Get all entities with their variations"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT entity_name, variations, usage_count, first_seen, last_seen
                    FROM entities
                    ORDER BY usage_count DESC
                """)
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'entity_name': row[0],
                        'variations': json.loads(row[1]) if row[1] else [],
                        'usage_count': row[2],
                        'first_seen': row[3],
                        'last_seen': row[4]
                    })
                
                return results
                
        except Exception as e:
            self.logger.log_activity(
                "get_entities_error",
                f"Error getting entities: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def store_document_context(self, file_path: str, entities: List[str], 
                             content_summary: str, keywords: List[str]):
        """Store document context for memory"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO document_context
                        (file_path, entities, content_summary, keywords)
                        VALUES (?, ?, ?, ?)
                    """, (
                        file_path, json.dumps(entities),
                        content_summary, json.dumps(keywords)
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.log_activity(
                "document_context_error",
                f"Error storing document context: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def search_related_documents(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for related documents based on keywords"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Create a query to search for documents with matching keywords
                keyword_placeholders = ','.join(['?' for _ in keywords])
                query = f"""
                    SELECT DISTINCT fa.file_path, fa.entities, fa.suggested_name,
                           COUNT(*) as match_count
                    FROM file_analysis fa
                    JOIN document_context dc ON fa.file_path = dc.file_path
                    WHERE dc.keywords LIKE '%' || ? || '%'
                    GROUP BY fa.file_path
                    ORDER BY match_count DESC
                    LIMIT ?
                """
                
                # For simplicity, we'll search for any keyword match
                results = []
                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    cursor.execute(query, (keyword, limit))
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        results.append({
                            'file_path': row[0],
                            'entities': json.loads(row[1]) if row[1] else [],
                            'suggested_name': row[2],
                            'similarity_score': row[3] / len(keywords)
                        })
                
                # Remove duplicates and sort by similarity
                unique_results = {}
                for result in results:
                    path = result['file_path']
                    if path not in unique_results or result['similarity_score'] > unique_results[path]['similarity_score']:
                        unique_results[path] = result
                
                final_results = sorted(unique_results.values(), 
                                     key=lambda x: x['similarity_score'], reverse=True)
                
                return final_results[:limit]
                
        except Exception as e:
            self.logger.log_activity(
                "related_documents_search_error",
                f"Error searching related documents: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def get_activity_timeline(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get activity timeline for the specified number of days"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute("""
                    SELECT activity_type, description, metadata, timestamp
                    FROM activity_log
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_date.isoformat(),))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'activity_type': row[0],
                        'description': row[1],
                        'metadata': json.loads(row[2]) if row[2] else {},
                        'timestamp': row[3]
                    })
                
                return results
                
        except Exception as e:
            self.logger.log_activity(
                "activity_timeline_error",
                f"Error getting activity timeline: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total files processed
                cursor.execute("SELECT COUNT(*) FROM file_analysis")
                stats['total_files'] = cursor.fetchone()[0]
                
                # Pending reviews
                cursor.execute("SELECT COUNT(*) FROM file_analysis WHERE status = 'pending'")
                stats['pending_reviews'] = cursor.fetchone()[0]
                
                # Total entities
                cursor.execute("SELECT COUNT(*) FROM entities")
                stats['total_entities'] = cursor.fetchone()[0]
                
                # Total activities
                cursor.execute("SELECT COUNT(*) FROM activity_log")
                stats['total_activities'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            self.logger.log_activity(
                "database_stats_error",
                f"Error getting database stats: {str(e)}",
                {"error": str(e)}
            )
            return {}
    
    def is_file_recently_processed(self, file_path: str, hours: int = 1) -> bool:
        """Check if file was processed recently"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                cursor.execute("""
                    SELECT COUNT(*) FROM processing_history
                    WHERE file_path = ? AND last_processed >= ?
                """, (file_path, cutoff_time.isoformat()))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            return False
    
    def clear_all_data(self):
        """Clear all data from the database"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Clear all tables
                    tables = ['file_analysis', 'entities', 'document_context', 
                             'activity_log', 'processing_history']
                    
                    for table in tables:
                        cursor.execute(f"DELETE FROM {table}")
                    
                    conn.commit()
                    
            self.logger.log_activity(
                "database_cleared",
                "All database data cleared",
                {}
            )
            
        except Exception as e:
            self.logger.log_activity(
                "database_clear_error",
                f"Error clearing database: {str(e)}",
                {"error": str(e)}
            )
            raise
    
    def add_entity_variation(self, canonical_name: str, variation: str):
        """Add a variation to an existing entity"""
        try:
            with self._lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Get current variations
                    cursor.execute("SELECT variations FROM entities WHERE entity_name = ?", 
                                 (canonical_name,))
                    row = cursor.fetchone()
                    
                    if row:
                        current_variations = json.loads(row[0]) if row[0] else []
                        if variation not in current_variations:
                            current_variations.append(variation)
                            
                            cursor.execute("""
                                UPDATE entities
                                SET variations = ?, last_seen = ?
                                WHERE entity_name = ?
                            """, (json.dumps(current_variations), 
                                 datetime.now().isoformat(), canonical_name))
                            
                            conn.commit()
                    
        except Exception as e:
            self.logger.log_activity(
                "entity_variation_add_error",
                f"Error adding entity variation: {str(e)}",
                {"canonical_name": canonical_name, "variation": variation, "error": str(e)}
            )
    
    def search_documents_by_entity(self, entity_name: str) -> List[Dict[str, Any]]:
        """Search documents by entity name"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_path, original_name, suggested_name, entities, created_at
                    FROM file_analysis
                    WHERE entities LIKE '%' || ? || '%'
                    ORDER BY created_at DESC
                """, (entity_name,))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    results.append({
                        'file_path': row[0],
                        'original_name': row[1],
                        'suggested_name': row[2],
                        'entities': json.loads(row[3]) if row[3] else [],
                        'created_at': row[4]
                    })
                
                return results
                
        except Exception as e:
            self.logger.log_activity(
                "entity_search_error",
                f"Error searching documents by entity: {str(e)}",
                {"entity_name": entity_name, "error": str(e)}
            )
            return []
    
    def get_top_entities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top entities by usage count"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT entity_name, usage_count
                    FROM entities
                    ORDER BY usage_count DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [{'entity_name': row[0], 'usage_count': row[1]} for row in rows]
                
        except Exception as e:
            return []
    
    def get_recent_entities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recently used entities"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT entity_name, last_seen
                    FROM entities
                    ORDER BY last_seen DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [{'entity_name': row[0], 'last_seen': row[1]} for row in rows]
                
        except Exception as e:
            return []
