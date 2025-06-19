import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from .context_memory import ContextMemory
from utils.logging_utils import LoggingUtils

class AIAnalyzer:
    """AI-powered content analysis and file naming"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.logger = LoggingUtils()
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def analyze_file_content(self, content: str, metadata: Dict[str, Any], 
                           context_memory: ContextMemory) -> Dict[str, Any]:
        """Analyze file content and generate naming suggestions"""
        try:
            # Get relevant context from memory
            context_info = context_memory.get_relevant_context(content, limit=5)
            
            # Prepare context information for the prompt
            context_text = ""
            if context_info:
                context_text = "\n\nRelevant context from previous documents:\n"
                for ctx in context_info:
                    context_text += f"- File: {ctx['file_path']}, Entities: {ctx['entities']}\n"
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(content, metadata, context_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyzer specializing in intelligent file naming and entity extraction. Your task is to analyze document content and suggest descriptive, consistent file names following the format: YYYY-MM-DD_EntityName_DescriptiveWords. Always maintain consistency with previously identified entities."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and structure the result
            analysis_result = {
                "suggested_name": result.get("suggested_name", ""),
                "entities": result.get("entities", []),
                "confidence": min(max(result.get("confidence", 0.5), 0.0), 1.0),
                "reasoning": result.get("reasoning", ""),
                "date": result.get("date", datetime.now().strftime("%Y-%m-%d")),
                "keywords": result.get("keywords", [])
            }
            
            self.logger.log_activity(
                "ai_analysis_complete",
                f"AI analysis completed for file",
                {
                    "suggested_name": analysis_result["suggested_name"],
                    "entities": analysis_result["entities"],
                    "confidence": analysis_result["confidence"]
                }
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.log_activity(
                "ai_analysis_error",
                f"Error in AI analysis: {str(e)}",
                {"error": str(e)}
            )
            
            # Return fallback result
            return {
                "suggested_name": f"{datetime.now().strftime('%Y-%m-%d')}_Unknown_Document",
                "entities": [],
                "confidence": 0.1,
                "reasoning": f"AI analysis failed: {str(e)}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "keywords": []
            }
    
    def _create_analysis_prompt(self, content: str, metadata: Dict[str, Any], 
                              context_text: str) -> str:
        """Create a detailed prompt for content analysis"""
        
        # Truncate content if too long (keep first 3000 chars)
        truncated_content = content[:3000] + "..." if len(content) > 3000 else content
        
        prompt = f"""
Analyze the following document content and provide a JSON response with intelligent file naming suggestions.

Document Content:
{truncated_content}

File Metadata:
- Original filename: {metadata.get('file_name', 'unknown')}
- File type: {metadata.get('extension', 'unknown')}
- File size: {metadata.get('file_size', 0)} bytes
- Created: {datetime.fromtimestamp(metadata.get('created_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if metadata.get('created_time') else 'unknown'}

{context_text}

Instructions:
1. Extract the document date (if mentioned) or use today's date: {datetime.now().strftime('%Y-%m-%d')}
2. Identify key entities (people, companies, organizations, clients)
3. Generate 2-4 descriptive keywords that capture the document's essence
4. Create a filename following this format: YYYY-MM-DD_EntityName_DescriptiveWords
5. Maintain consistency with entities from context (use same names for same entities)
6. Ensure the filename is filesystem-safe (no special characters except underscore and hyphen)

Respond with JSON in this exact format:
{{
    "suggested_name": "2024-06-19_ClientName_ContractReview",
    "entities": ["ClientName", "CompanyName"],
    "confidence": 0.85,
    "reasoning": "Document appears to be a contract review for ClientName, dated June 19, 2024",
    "date": "2024-06-19",
    "keywords": ["contract", "review", "legal", "agreement"]
}}
"""
        return prompt
    
    def generate_embedding(self, content: str) -> List[float]:
        """Generate vector embedding for content"""
        try:
            # Truncate content if too long for embedding
            truncated_content = content[:8000] if len(content) > 8000 else content
            
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=truncated_content
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.log_activity(
                "embedding_error",
                f"Error generating embedding: {str(e)}",
                {"error": str(e)}
            )
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def analyze_image_content(self, image_base64: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image content using GPT-4 Vision"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Analyze this image and extract any visible text, identify key elements, and suggest a descriptive filename.
                                
Respond with JSON in this format:
{{
    "suggested_name": "YYYY-MM-DD_EntityName_Description",
    "entities": ["extracted entities"],
    "confidence": 0.85,
    "reasoning": "explanation of analysis",
    "visible_text": "any text found in image",
    "image_description": "description of what's shown",
    "keywords": ["relevant", "keywords"]
}}

Original filename: {metadata.get('file_name', 'unknown')}
Use today's date {datetime.now().strftime('%Y-%m-%d')} if no date is visible in the image."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Structure the result
            analysis_result = {
                "suggested_name": result.get("suggested_name", f"{datetime.now().strftime('%Y-%m-%d')}_Image_Document"),
                "entities": result.get("entities", []),
                "confidence": min(max(result.get("confidence", 0.5), 0.0), 1.0),
                "reasoning": result.get("reasoning", ""),
                "visible_text": result.get("visible_text", ""),
                "image_description": result.get("image_description", ""),
                "keywords": result.get("keywords", [])
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.log_activity(
                "image_analysis_error",
                f"Error in image analysis: {str(e)}",
                {"error": str(e)}
            )
            
            return {
                "suggested_name": f"{datetime.now().strftime('%Y-%m-%d')}_Image_Unknown",
                "entities": [],
                "confidence": 0.1,
                "reasoning": f"Image analysis failed: {str(e)}",
                "visible_text": "",
                "image_description": "Analysis failed",
                "keywords": []
            }
