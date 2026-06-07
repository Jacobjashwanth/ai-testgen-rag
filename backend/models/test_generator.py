import anthropic
from typing import List, Tuple
from .file_parser import Chunk

class TestGenerator:
    """Generate test cases using Claude API."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate_tests(self, query: str, chunks: List[Tuple[Chunk, float]],
                      test_types: List[str]) -> List[dict]:
        """Generate test cases for given chunks."""
        if not chunks:
            return []
        
        # Format chunks for context
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
        """Format retrieved chunks for Claude context."""
        context_parts = []
        for i, (chunk, similarity) in enumerate(chunks, 1):
            context_parts.append(f"""
--- Chunk {i} (Similarity: {similarity:.2f}) ---
File: {chunk.source_file}
Type: {chunk.chunk_type}
Name: {chunk.name}
Lines: {chunk.line_start}-{chunk.line_end}

```
{chunk.content}
```
""")
        return '\n'.join(context_parts)
    
    def _generate_test_for_type(self, query: str, context: str, test_type: str) -> str:
        """Generate test code for a specific test type."""
        
        prompts = {
            'pytest': self._prompt_pytest,
            'selenium': self._prompt_selenium,
            'rest': self._prompt_rest
        }
        
        prompt_fn = prompts.get(test_type, self._prompt_pytest)
        system_prompt = self._get_system_prompt(test_type)
        user_prompt = prompt_fn(query, context)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating test: {str(e)}"
    
    def _get_system_prompt(self, test_type: str) -> str:
        """Get system prompt for test generation."""
        if test_type == 'pytest':
            return """You are an expert Python test engineer. Generate comprehensive pytest unit tests
based on the provided code snippets. Include docstrings, fixtures, and edge cases."""
        elif test_type == 'selenium':
            return """You are an expert Selenium test automation engineer. Generate Selenium tests
for web UI automation based on the provided context. Include proper waits and error handling."""
        elif test_type == 'rest':
            return """You are an expert API test engineer. Generate REST API tests using pytest and requests.
Include positive, negative, and edge case scenarios."""
        return "Generate high-quality tests."
    
    def _prompt_pytest(self, query: str, context: str) -> str:
        return f"""Based on the following code snippets and query, generate comprehensive pytest unit tests.

Query: {query}

Code Context:
{context}

Generate pytest test cases that:
1. Test the main functionality
2. Include edge cases and error scenarios
3. Use pytest fixtures where appropriate
4. Include clear docstrings
5. Follow pytest best practices

Return ONLY the test code, no explanations."""
    
    def _prompt_selenium(self, query: str, context: str) -> str:
        return f"""Based on the following context and query, generate Selenium UI tests.

Query: {query}

Context:
{context}

Generate Selenium tests that:
1. Use WebDriverWait for proper synchronization
2. Include proper error handling
3. Test user interactions (click, fill, submit)
4. Verify expected results
5. Include setup and teardown

Return ONLY the test code, no explanations."""
    
    def _prompt_rest(self, query: str, context: str) -> str:
        return f"""Based on the following API specification and query, generate REST API tests.

Query: {query}

API Context:
{context}

Generate pytest tests that:
1. Test all HTTP methods (GET, POST, PUT, DELETE)
2. Include positive and negative test cases
3. Validate response status codes and body
4. Test error scenarios
5. Include parameterized tests for multiple scenarios

Return ONLY the test code, no explanations."""
