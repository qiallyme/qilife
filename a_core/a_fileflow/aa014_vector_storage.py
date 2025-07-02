import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sqlite3
from datetime import datetime

# Try importing numpy with fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    import faiss
except ImportError:
    faiss = None

from a_core.e_utils.ae02_logging_utils import LoggingUtils

class VectorStorage:
    """Vector database for semantic storage and search"""
    
    def __init__(self, storage_path: str = "./vector_db"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.logger = LoggingUtils()
        
        # Initialize the vector database
        self.client = None
        self.collection = None
        self.faiss_index = None
        self.metadata_db = None
        
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize the vector storage system"""
        try:
            # Try ChromaDB first
            if chromadb:
                self._initialize_chromadb()
            elif faiss:
                self._initialize_faiss()
            else:
                self._initialize_sqlite_fallback()
                
        except Exception as e:
            self.logger.log_activity(
                "vector_storage_init_error",
                f"Error initializing vector storage: {str(e)}",
                {"error": str(e)}
            )
            # Fallback to SQLite-based storage
            self._initialize_sqlite_fallback()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB for vector storage"""
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path / "chroma_db"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="document_embeddings",
                metadata={"description": "Document content embeddings for semantic search"}
            )
            
            self.logger.log_activity(
                "vector_storage_init",
                "ChromaDB initialized successfully",
                {"storage_path": str(self.storage_path)}
            )
            
        except Exception as e:
            raise Exception(f"ChromaDB initialization failed: {str(e)}")
    
    def _initialize_faiss(self):
        """Initialize FAISS for vector storage"""
        try:
            # Create FAISS index (using 1536 dimensions for OpenAI embeddings)
            self.faiss_index = faiss.IndexFlatL2(1536)
            
            # Create metadata database
            metadata_db_path = self.storage_path / "metadata.db"
            self.metadata_db = sqlite3.connect(str(metadata_db_path), check_same_thread=False)
            
            # Create metadata table
            cursor = self.metadata_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vector_id TEXT UNIQUE,
                    content TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.metadata_db.commit()
            
            # Load existing index if it exists
            index_path = self.storage_path / "faiss_index.bin"
            if index_path.exists():
                self.faiss_index = faiss.read_index(str(index_path))
            
            self.logger.log_activity(
                "vector_storage_init",
                "FAISS initialized successfully",
                {"storage_path": str(self.storage_path)}
            )
            
        except Exception as e:
            raise Exception(f"FAISS initialization failed: {str(e)}")
    
    def _initialize_sqlite_fallback(self):
        """Initialize SQLite fallback for vector storage"""
        try:
            db_path = self.storage_path / "vectors.db"
            self.metadata_db = sqlite3.connect(str(db_path), check_same_thread=False)
            
            cursor = self.metadata_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vector_id TEXT UNIQUE,
                    embedding TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.metadata_db.commit()
            
            self.logger.log_activity(
                "vector_storage_init",
                "SQLite fallback initialized successfully",
                {"storage_path": str(self.storage_path)}
            )
            
        except Exception as e:
            raise Exception(f"SQLite fallback initialization failed: {str(e)}")
    
    def store_embedding(self, embedding: List[float], content: str, 
                       metadata: Dict[str, Any]) -> str:
        """Store an embedding with its content and metadata"""
        try:
            vector_id = f"vec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            if self.collection:  # ChromaDB
                self.collection.add(
                    embeddings=[embedding],
                    documents=[content[:1000]],  # ChromaDB has document length limits
                    metadatas=[metadata],
                    ids=[vector_id]
                )
                
            elif self.faiss_index is not None:  # FAISS
                # Add to FAISS index
                if NUMPY_AVAILABLE and np is not None:
                    embedding_array = np.array([embedding], dtype=np.float32)
                    self.faiss_index.add(embedding_array)
                else:
                    # If numpy not available, fall back to SQLite storage
                    cursor = self.metadata_db.cursor()
                    cursor.execute("""
                        INSERT INTO vectors (vector_id, embedding, content, metadata)
                        VALUES (?, ?, ?, ?)
                    """, (vector_id, json.dumps(embedding), content, json.dumps(metadata)))
                    self.metadata_db.commit()
                    return vector_id
                
                # Store metadata
                cursor = self.metadata_db.cursor()
                cursor.execute("""
                    INSERT INTO vector_metadata (vector_id, content, metadata)
                    VALUES (?, ?, ?)
                """, (vector_id, content, json.dumps(metadata)))
                self.metadata_db.commit()
                
                # Save FAISS index
                index_path = self.storage_path / "faiss_index.bin"
                faiss.write_index(self.faiss_index, str(index_path))
                
            else:  # SQLite fallback
                cursor = self.metadata_db.cursor()
                cursor.execute("""
                    INSERT INTO vectors (vector_id, embedding, content, metadata)
                    VALUES (?, ?, ?, ?)
                """, (vector_id, json.dumps(embedding), content, json.dumps(metadata)))
                self.metadata_db.commit()
            
            self.logger.log_activity(
                "embedding_stored",
                f"Embedding stored with ID: {vector_id}",
                {"vector_id": vector_id, "content_length": len(content)}
            )
            
            return vector_id
            
        except Exception as e:
            self.logger.log_activity(
                "embedding_storage_error",
                f"Error storing embedding: {str(e)}",
                {"error": str(e)}
            )
            raise
    
    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        try:
            results = []
            
            if self.collection:  # ChromaDB
                query_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit
                )
                
                for i in range(len(query_results['ids'][0])):
                    results.append({
                        'id': query_results['ids'][0][i],
                        'content': query_results['documents'][0][i],
                        'metadata': query_results['metadatas'][0][i],
                        'distance': query_results['distances'][0][i] if 'distances' in query_results else 0
                    })
                    
            elif self.faiss_index is not None:  # FAISS
                if NUMPY_AVAILABLE and np is not None:
                    query_array = np.array([query_embedding], dtype=np.float32)
                    distances, indices = self.faiss_index.search(query_array, limit)
                else:
                    # Fall back to SQLite similarity search
                    cursor = self.metadata_db.cursor()
                    cursor.execute("SELECT vector_id, embedding, content, metadata FROM vectors")
                    
                    all_vectors = cursor.fetchall()
                    similarities = []
                    
                    for row in all_vectors:
                        stored_embedding = json.loads(row[1])
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)
                        similarities.append({
                            'id': row[0],
                            'content': row[2],
                            'metadata': json.loads(row[3]),
                            'distance': 1 - similarity
                        })
                    
                    similarities.sort(key=lambda x: x['distance'])
                    return similarities[:limit]
                
                cursor = self.metadata_db.cursor()
                for i, idx in enumerate(indices[0]):
                    if idx != -1:  # Valid result
                        cursor.execute("""
                            SELECT vector_id, content, metadata
                            FROM vector_metadata
                            ORDER BY id
                            LIMIT 1 OFFSET ?
                        """, (int(idx),))
                        
                        row = cursor.fetchone()
                        if row:
                            results.append({
                                'id': row[0],
                                'content': row[1],
                                'metadata': json.loads(row[2]),
                                'distance': float(distances[0][i])
                            })
                            
            else:  # SQLite fallback (cosine similarity calculation)
                cursor = self.metadata_db.cursor()
                cursor.execute("SELECT vector_id, embedding, content, metadata FROM vectors")
                
                all_vectors = cursor.fetchall()
                similarities = []
                
                for row in all_vectors:
                    stored_embedding = json.loads(row[1])
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    similarities.append({
                        'id': row[0],
                        'content': row[2],
                        'metadata': json.loads(row[3]),
                        'distance': 1 - similarity  # Convert similarity to distance
                    })
                
                # Sort by distance (ascending) and take top results
                similarities.sort(key=lambda x: x['distance'])
                results = similarities[:limit]
            
            return results
            
        except Exception as e:
            self.logger.log_activity(
                "vector_search_error",
                f"Error searching vectors: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if NUMPY_AVAILABLE and np is not None:
                vec1_np = np.array(vec1)
                vec2_np = np.array(vec2)
                
                dot_product = np.dot(vec1_np, vec2_np)
                norm1 = np.linalg.norm(vec1_np)
                norm2 = np.linalg.norm(vec2_np)
                
                if norm1 == 0 or norm2 == 0:
                    return 0
                    
                return dot_product / (norm1 * norm2)
            else:
                # Fallback implementation without numpy
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = sum(a * a for a in vec1) ** 0.5
                norm2 = sum(b * b for b in vec2) ** 0.5
                
                if norm1 == 0 or norm2 == 0:
                    return 0
                    
                return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0
    
    def get_total_embeddings(self) -> int:
        """Get total number of stored embeddings"""
        try:
            if self.collection:
                return self.collection.count()
            elif self.metadata_db:
                cursor = self.metadata_db.cursor()
                if self.faiss_index is not None:
                    cursor.execute("SELECT COUNT(*) FROM vector_metadata")
                else:
                    cursor.execute("SELECT COUNT(*) FROM vectors")
                return cursor.fetchone()[0]
            return 0
        except Exception:
            return 0
    
    def clear_all_vectors(self):
        """Clear all stored vectors"""
        try:
            if self.collection:
                # Delete and recreate collection
                self.client.delete_collection("document_embeddings")
                self.collection = self.client.create_collection(
                    name="document_embeddings",
                    metadata={"description": "Document content embeddings for semantic search"}
                )
            elif self.faiss_index is not None:
                # Reset FAISS index
                self.faiss_index = faiss.IndexFlatL2(1536)
                cursor = self.metadata_db.cursor()
                cursor.execute("DELETE FROM vector_metadata")
                self.metadata_db.commit()
            else:
                cursor = self.metadata_db.cursor()
                cursor.execute("DELETE FROM vectors")
                self.metadata_db.commit()
                
            self.logger.log_activity(
                "vectors_cleared",
                "All vectors cleared successfully",
                {}
            )
            
        except Exception as e:
            self.logger.log_activity(
                "vector_clear_error",
                f"Error clearing vectors: {str(e)}",
                {"error": str(e)}
            )
            raise
    
    def rebuild_index(self):
        """Rebuild the vector index (useful for FAISS)"""
        try:
            if self.faiss_index is not None and self.metadata_db:
                # Create new index
                self.faiss_index = faiss.IndexFlatL2(1536)
                
                # Reload all vectors
                if NUMPY_AVAILABLE and np is not None:
                    cursor = self.metadata_db.cursor()
                    cursor.execute("SELECT embedding FROM vector_metadata ORDER BY id")
                    
                    embeddings = []
                    for row in cursor.fetchall():
                        embedding = json.loads(row[0])
                        embeddings.append(embedding)
                    
                    if embeddings:
                        embeddings_array = np.array(embeddings, dtype=np.float32)
                        self.faiss_index.add(embeddings_array)
                else:
                    # Cannot rebuild FAISS index without numpy
                    self.logger.log_activity(
                        "index_rebuild_skipped",
                        "FAISS index rebuild skipped - numpy not available",
                        {"numpy_available": False}
                    )
                    return
                    
                    # Save rebuilt index
                    index_path = self.storage_path / "faiss_index.bin"
                    faiss.write_index(self.faiss_index, str(index_path))
                
                self.logger.log_activity(
                    "index_rebuilt",
                    f"Vector index rebuilt with {len(embeddings)} vectors",
                    {"vector_count": len(embeddings)}
                )
            
        except Exception as e:
            self.logger.log_activity(
                "index_rebuild_error",
                f"Error rebuilding index: {str(e)}",
                {"error": str(e)}
            )
            raise
