from typing import List, Tuple

import anthropic
import httpx
from services.file_parser import Chunk


class TestGenerator:
    """Generate test cases using Claude API with Ollama fallback."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.claude_model = "claude-3-5-sonnet-20241022"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3"

    def generate_tests(self, query: str, chunks: List[Tuple[Chunk, float]],
                       test_types: List[str]) -> List[dict]:
        if not chunks:
            return []
        context = self._format_context(chunks)
        tests = []
        for test_type in test_types:
            test_code = self._generate_test_for_type(query, context, test_type)
            tests.append({
                'test_type': test_type,
                'test_code': test_code,
                'citations': [chunk for chunk, _ in chunks]
            })
        return tests

    def _format_context(self, chunks: List[Tuple[Chunk, float]]) -> str:
        parts = []
        for i, (chunk, similarity) in enumerate(chunks, 1):
            parts.append(f"""
--- Chunk {i} (Similarity: {similarity:.2f}) ---
File: {chunk.source_file} | Type: {chunk.chunk_type} | Name: {chunk.name}
{chunk.content}
""")
        return '\n'.join(parts)

    def _generate_test_for_type(self, query: str, context: str, test_type: str) -> str:
        system_prompt = self._get_system_prompt(test_type)
        prompt_fn = {
            'pytest': self._prompt_pytest,
            'selenium': self._prompt_selenium,
            'rest': self._prompt_rest,
        }.get(test_type, self._prompt_pytest)
        user_prompt = prompt_fn(query, context)

        # Try Claude first
        if self.api_key:
            try:
                client = anthropic.Anthropic(api_key=self.api_key)
                message = client.messages.create(
                    model=self.claude_model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                print(f"[INFO] Generated with Claude")
                return message.content[0].text
            except Exception as e:
                print(f"[WARN] Claude failed: {e} — trying Ollama fallback")

        # Fallback to Ollama
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            with httpx.Client(timeout=120) as client:
                r = client.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "prompt": full_prompt,
                    "stream": False,
                })
                r.raise_for_status()
                print(f"[INFO] Generated with Ollama/{self.ollama_model}")
                return r.json().get("response", "No response from Ollama")
        except Exception as e:
            return (
                f"# Both Claude and Ollama failed\n"
                f"# Claude: no credits — add at console.anthropic.com\n"
                f"# Ollama error: {e}\n"
                f"# Fix: run 'ollama pull llama3' in terminal"
            )

    def _get_system_prompt(self, test_type: str) -> str:
        if test_type == 'pytest':
            return "You are an expert Python test engineer. Generate comprehensive pytest unit tests with docstrings, fixtures, and edge cases."
        elif test_type == 'selenium':
            return "You are an expert Selenium test automation engineer. Generate Selenium tests with WebDriverWait and proper error handling."
        elif test_type == 'rest':
            return "You are an expert API test engineer. Generate REST API tests using pytest and requests with positive and negative cases."
        return "Generate high-quality tests."

    def _prompt_pytest(self, query: str, context: str) -> str:
        return f"""Query: {query}

Code Context:
{context}

Generate complete pytest test cases. Return ONLY the test code."""

    def _prompt_selenium(self, query: str, context: str) -> str:
        return f"""Query: {query}

Context:
{context}

Generate complete Selenium tests. Return ONLY the test code."""

    def _prompt_rest(self, query: str, context: str) -> str:
        return f"""Query: {query}

API Context:
{context}

Generate complete REST API tests. Return ONLY the test code."""