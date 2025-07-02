import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from a_core.a_fileflow.aa05_database import DatabaseManager
from a_core.e_utils.ae02_logging_utils import LoggingUtils

class ContextMemory:
    """Maintain context and consistency across document processing"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = LoggingUtils()
        
        # Entity consistency tracking
        self.entity_cache = {}
        self.load_entity_cache()
    
    def load_entity_cache(self):
        """Load entity mappings from database"""
        try:
            entities = self.db_manager.get_all_entities()
            self.entity_cache = {}
            
            for entity_data in entities:
                entity_name = entity_data['entity_name']
                variations = entity_data.get('variations', [])
                
                # Map all variations to the canonical name
                self.entity_cache[entity_name.lower()] = entity_name
                for variation in variations:
                    self.entity_cache[variation.lower()] = entity_name
                    
        except Exception as e:
            self.logger.log_activity(
                "entity_cache_load_error",
                f"Error loading entity cache: {str(e)}",
                {"error": str(e)}
            )
            self.entity_cache = {}
    
    def get_relevant_context(self, content: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context from previous documents"""
        try:
            # Extract potential entities and keywords from current content
            keywords = self._extract_keywords(content)
            
            # Search for related documents
            related_docs = self.db_manager.search_related_documents(keywords, limit)
            
            context_info = []
            for doc in related_docs:
                context_info.append({
                    'file_path': doc['file_path'],
                    'entities': doc['entities'],
                    'suggested_name': doc['suggested_name'],
                    'similarity_score': doc.get('similarity_score', 0.5)
                })
            
            return context_info
            
        except Exception as e:
            self.logger.log_activity(
                "context_retrieval_error",
                f"Error retrieving context: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract potential keywords from content"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        words = content.lower().split()
        
        # Filter out common words and get unique keywords
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall'}
        
        keywords = []
        for word in words:
            # Clean word
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 3 and clean_word not in stop_words:
                keywords.append(clean_word)
        
        # Return top 20 most frequent keywords
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]
    
    def normalize_entity_name(self, entity_name: str) -> str:
        """Normalize entity name for consistency"""
        try:
            # Check if we've seen this entity or a variation before
            normalized_key = entity_name.lower().strip()
            
            if normalized_key in self.entity_cache:
                return self.entity_cache[normalized_key]
            
            # Check for partial matches
            for cached_key, canonical_name in self.entity_cache.items():
                if self._entities_similar(normalized_key, cached_key):
                    # Add this variation to our cache
                    self.entity_cache[normalized_key] = canonical_name
                    self._update_entity_variations(canonical_name, entity_name)
                    return canonical_name
            
            # New entity - add to cache
            canonical_name = self._canonicalize_entity_name(entity_name)
            self.entity_cache[normalized_key] = canonical_name
            self._store_new_entity(canonical_name, [entity_name])
            
            return canonical_name
            
        except Exception as e:
            self.logger.log_activity(
                "entity_normalization_error",
                f"Error normalizing entity: {str(e)}",
                {"entity_name": entity_name, "error": str(e)}
            )
            return entity_name
    
    def _entities_similar(self, entity1: str, entity2: str) -> bool:
        """Check if two entity names are similar"""
        # Simple similarity check - can be enhanced with fuzzy matching
        entity1_words = set(entity1.split())
        entity2_words = set(entity2.split())
        
        # Check for significant word overlap
        common_words = entity1_words.intersection(entity2_words)
        min_words = min(len(entity1_words), len(entity2_words))
        
        if min_words == 0:
            return False
            
        similarity_ratio = len(common_words) / min_words
        return similarity_ratio > 0.7  # 70% word overlap threshold
    
    def _canonicalize_entity_name(self, entity_name: str) -> str:
        """Create a canonical form of the entity name"""
        # Basic canonicalization - title case, remove extra spaces
        return ' '.join(word.capitalize() for word in entity_name.split())
    
    def _store_new_entity(self, canonical_name: str, variations: List[str]):
        """Store a new entity in the database"""
        try:
            self.db_manager.store_entity(canonical_name, variations)
        except Exception as e:
            self.logger.log_activity(
                "entity_storage_error",
                f"Error storing new entity: {str(e)}",
                {"canonical_name": canonical_name, "error": str(e)}
            )
    
    def _update_entity_variations(self, canonical_name: str, new_variation: str):
        """Add a new variation to an existing entity"""
        try:
            self.db_manager.add_entity_variation(canonical_name, new_variation)
        except Exception as e:
            self.logger.log_activity(
                "entity_variation_update_error",
                f"Error updating entity variations: {str(e)}",
                {"canonical_name": canonical_name, "new_variation": new_variation, "error": str(e)}
            )
    
    def update_context(self, entities: List[str], content: str, file_path: str):
        """Update context memory with new document information"""
        try:
            # Normalize all entities
            normalized_entities = []
            for entity in entities:
                normalized = self.normalize_entity_name(entity)
                normalized_entities.append(normalized)
            
            # Store document context
            self.db_manager.store_document_context(
                file_path=file_path,
                entities=normalized_entities,
                content_summary=content[:500],  # Store first 500 chars as summary
                keywords=self._extract_keywords(content)[:10]  # Top 10 keywords
            )
            
            self.logger.log_activity(
                "context_updated",
                f"Context updated for file: {file_path}",
                {
                    "file_path": file_path,
                    "entities": normalized_entities,
                    "keyword_count": len(self._extract_keywords(content)[:10])
                }
            )
            
        except Exception as e:
            self.logger.log_activity(
                "context_update_error",
                f"Error updating context: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about entity usage"""
        try:
            return {
                'total_entities': len(self.entity_cache),
                'top_entities': self.db_manager.get_top_entities(limit=10),
                'recent_entities': self.db_manager.get_recent_entities(limit=5)
            }
        except Exception as e:
            self.logger.log_activity(
                "entity_stats_error",
                f"Error getting entity statistics: {str(e)}",
                {"error": str(e)}
            )
            return {'total_entities': 0, 'top_entities': [], 'recent_entities': []}
    
    def search_by_entity(self, entity_name: str) -> List[Dict[str, Any]]:
        """Search for documents by entity name"""
        try:
            # Normalize the search entity
            normalized_entity = self.normalize_entity_name(entity_name)
            
            # Search for documents containing this entity
            return self.db_manager.search_documents_by_entity(normalized_entity)
            
        except Exception as e:
            self.logger.log_activity(
                "entity_search_error",
                f"Error searching by entity: {str(e)}",
                {"entity_name": entity_name, "error": str(e)}
            )
            return []
