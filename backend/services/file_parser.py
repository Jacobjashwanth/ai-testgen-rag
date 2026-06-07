import ast
import inspect
from typing import List, Tuple

class Chunk:
    def __init__(self, content: str, source_file: str, line_start: int, line_end: int,
                 chunk_type: str, name: str):
        self.content = content
        self.source_file = source_file
        self.line_start = line_start
        self.line_end = line_end
        self.chunk_type = chunk_type
        self.name = name

class PythonFileParser:
    """Parse Python files into chunks by function/class using AST."""
    
    @staticmethod
    def parse_file(filepath: str, file_content: str) -> List[Chunk]:
        """Parse a Python file and extract functions/classes as chunks."""
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")
        
        chunks = []
        lines = file_content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                chunk_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                
                # Get source code for this node
                start_line = node.lineno - 1
                end_line = node.end_lineno
                
                # Extract source lines
                source_lines = lines[start_line:end_line]
                source_code = '\n'.join(source_lines)
                
                chunk = Chunk(
                    content=source_code,
                    source_file=filepath,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    chunk_type=chunk_type,
                    name=node.name
                )
                chunks.append(chunk)
        
        return chunks

class SpecParser:
    """Parse OpenAPI/REST API specs."""
    
    @staticmethod
    def parse_spec(spec_content: str, spec_type: str = 'openapi') -> List[Chunk]:
        """Parse API specification into chunks."""
        chunks = []
        
        if spec_type == 'openapi' or spec_type == 'json':
            import json
            try:
                spec = json.loads(spec_content)
                chunks = SpecParser._parse_openapi(spec, spec_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON spec: {e}")
        
        return chunks
    
    @staticmethod
    def _parse_openapi(spec: dict, raw_content: str) -> List[Chunk]:
        """Extract endpoints from OpenAPI spec as chunks."""
        chunks = []
        paths = spec.get('paths', {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    operation_id = details.get('operationId', f"{method}_{path}")
                    description = details.get('description', '')
                    parameters = details.get('parameters', [])
                    request_body = details.get('requestBody', {})
                    
                    content = f"{method.upper()} {path}\n{description}\n"
                    if parameters:
                        content += f"Parameters: {len(parameters)}\n"
                    if request_body:
                        content += "Has request body\n"
                    
                    chunk = Chunk(
                        content=content.strip(),
                        source_file="spec.json",
                        line_start=1,
                        line_end=1,
                        chunk_type="endpoint",
                        name=operation_id
                    )
                    chunks.append(chunk)
        
        return chunks

class FileParser:
    """Main file parser dispatcher."""
    
    @staticmethod
    def parse(filepath: str, content: str) -> List[Chunk]:
        """Parse file based on extension."""
        if filepath.endswith('.py'):
            return PythonFileParser.parse_file(filepath, content)
        elif filepath.endswith('.json') or filepath.endswith('.yaml') or filepath.endswith('.yml'):
            return SpecParser.parse_spec(content, 'openapi')
        else:
            raise ValueError(f"Unsupported file type: {filepath}")
