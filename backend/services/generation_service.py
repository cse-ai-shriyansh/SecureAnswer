"""
Generation Service - LLM-based answer generation
"""

import os
import time
from typing import List, Dict, Optional
from datetime import datetime
import json


class GenerationService:
    """
    RAG Generation Service - Handles LLM-based answer generation.

    Uses Google Gemini for answer generation.
    """
    
    def __init__(self, model: str = None, api_key: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize generation service.
        
        Args:
            model: LLM model identifier (defaults to env LLM_PROVIDER config)
            api_key: API key for LLM provider (defaults to environment variable)
            provider: LLM provider name (defaults to gemini)
        """
        # Detect provider from env if not specified
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # Set model based on provider
        if model is None:
            if self.provider_name == "gemini":
                model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            else:
                model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        self.model = model
        self.api_key = api_key
        self.client = None
        self.provider = None
        
        # Initialize provider-specific client
        if self.provider_name == "gemini":
            self._init_gemini()
        else:
            self._init_gemini()
        
        # Track generation stats
        self.generation_times = []
        self.total_generations = 0
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            from google import genai
            api_key = self.api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
                self.provider = "gemini"
                print(f"✓ Initialized Gemini client for model: {self.model}")
            else:
                print("Warning: GOOGLE_API_KEY (or GEMINI_API_KEY) not set")
        except ImportError:
            print("Warning: google-genai not available. Install with: pip install google-genai")
    
    def _build_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Build prompt with context for LLM.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            
        Returns:
            Formatted prompt string
        """
        # Limit number of context chunks and truncate long chunk text to avoid exceeding model context window
        max_chunks = 6
        max_chunk_chars = 1000
        safe_chunks = context_chunks[:max_chunks]
        context_parts = []
        for chunk in safe_chunks:
            text = chunk.get('text', '') or ''
            if len(text) > max_chunk_chars:
                text = text[:max_chunk_chars] + '...'
            context_parts.append(f"[Source: {chunk.get('source_file', 'unknown')}]\n{text}")

        context_text = "\n\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant answering questions based on the provided context.

    Context:
    {context_text}

    Question: {query}

    Provide a complete, detailed answer using the context above. If the context is insufficient, say so and provide a best-effort answer. Keep the answer self-contained and avoid cutting the response short."""
        
        return prompt
    
    def generate(
        self,
        query: str,
        context_chunks: List[Dict],
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate answer using LLM.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            
        Returns:
            Dictionary with answer, confidence, and metadata
        """
        start_time = time.time()
        
        # Build prompt
        prompt = self._build_prompt(query, context_chunks)
        
        # Generate with provider
        if self.provider == "gemini" and self.client:
            try:
                # Request generation with explicit decoding params
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.95,
                        "top_k": 40,
                    },
                )

                # Extract text safely — SDK exposes `.text` for text outputs
                answer = getattr(response, 'text', None)
                if not answer:
                    # Try to reconstruct from parts if available
                    parts = getattr(response, 'parts', None) or []
                    collected = []
                    for p in parts:
                        try:
                            # parts may contain inline_data or text; convert to str
                            collected.append(str(getattr(p, 'text', '') or p))
                        except Exception:
                            continue
                    answer = "\n".join([c for c in collected if c]) or self._fallback_answer(query, context_chunks)

                confidence_score = 0.9
                # Debug: print response length
                try:
                    print(f"Gemini response length: {len(answer)} chars")
                except Exception:
                    pass
            except Exception as e:
                print(f"Error calling Gemini: {e}")
                answer = self._fallback_answer(query, context_chunks)
                confidence_score = 0.5
        
        else:
            # Fallback response
            answer = self._fallback_answer(query, context_chunks)
            confidence_score = 0.6
        
        generation_time_ms = (time.time() - start_time) * 1000
        self.generation_times.append(generation_time_ms)
        self.total_generations += 1
        
        return {
            "answer": answer,
            "confidence_score": confidence_score,
            "model_used": self.model,
            "provider_used": self.provider or "fallback",
            "generation_time_ms": generation_time_ms,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _fallback_answer(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Generate fallback answer when LLM not available.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            
        Returns:
            Summary-based answer
        """
        if not context_chunks:
            return f"I couldn't find relevant information to answer: {query}"
        
        # Simple extractive answer from top chunk
        top_chunk = context_chunks[0]
        text = top_chunk.get("text", "")
        
        # Take first 300 characters as answer
        answer = text[:300] + "..." if len(text) > 300 else text
        
        return f"Based on the available documentation:\n\n{answer}"
    
    def get_stats(self) -> Dict:
        """Get generation service statistics"""
        if not self.generation_times:
            return {
                "model": self.model,
                "provider": self.provider or "none",
                "total_generations": 0,
                "avg_generation_time_ms": 0
            }
        
        return {
            "model": self.model,
            "provider": self.provider or "none",
            "total_generations": self.total_generations,
            "avg_generation_time_ms": sum(self.generation_times) / len(self.generation_times)
        }
