"""
Test file for demonstrating various Python patterns.
This file includes classes, functions, decorators, and async code.
"""

from typing import List, Optional, Callable
from functools import wraps
import asyncio


def timing_decorator(func: Callable) -> Callable:
    """Decorator that measures function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper


class Calculator:
    """Simple calculator class with various operations."""
    
    def __init__(self, precision: int = 2):
        self.precision = precision
        self.history: List[float] = []
    
    @timing_decorator
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = round(a + b, self.precision)
        self.history.append(result)
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = round(a * b, self.precision)
        self.history.append(result)
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers with error handling."""
        if b == 0:
            raise ValueError("Division by zero")
        result = round(a / b, self.precision)
        self.history.append(result)
        return result
    
    def get_history(self) -> List[float]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()


class DataProcessor:
    """Process and transform data."""
    
    def __init__(self, data: List[int]):
        self.data = data
    
    def filter_even(self) -> List[int]:
        """Return only even numbers."""
        return [x for x in self.data if x % 2 == 0]
    
    def filter_odd(self) -> List[int]:
        """Return only odd numbers."""
        return [x for x in self.data if x % 2 != 0]
    
    def transform(self, func: Callable[[int], int]) -> List[int]:
        """Apply transformation function to all data."""
        return [func(x) for x in self.data]
    
    def aggregate(self, operation: str = 'sum') -> float:
        """Aggregate data using specified operation."""
        if operation == 'sum':
            return sum(self.data)
        elif operation == 'avg':
            return sum(self.data) / len(self.data) if self.data else 0
        elif operation == 'max':
            return max(self.data) if self.data else None
        elif operation == 'min':
            return min(self.data) if self.data else None
        else:
            raise ValueError(f"Unknown operation: {operation}")


async def fetch_data(url: str, delay: float = 0.1) -> dict:
    """Async function to simulate data fetching."""
    await asyncio.sleep(delay)
    return {"url": url, "status": "success"}


async def batch_fetch(urls: List[str]) -> List[dict]:
    """Fetch multiple URLs concurrently."""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)


def parse_csv(csv_string: str) -> List[dict]:
    """Parse simple CSV format to list of dicts."""
    lines = csv_string.strip().split('\n')
    if not lines:
        return []
    
    headers = lines[0].split(',')
    rows = []
    
    for line in lines[1:]:
        values = line.split(',')
        row = {headers[i]: values[i] for i in range(len(headers))}
        rows.append(row)
    
    return rows


@timing_decorator
def bubble_sort(arr: List[int]) -> List[int]:
    """Bubble sort implementation."""
    n = len(arr)
    result = arr.copy()
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result


class Logger:
    """Simple logging utility."""
    
    def __init__(self, name: str):
        self.name = name
        self.logs: List[str] = []
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logs.append(f"[INFO] {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logs.append(f"[WARNING] {message}")
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logs.append(f"[ERROR] {message}")
    
    def get_logs(self) -> List[str]:
        """Get all logs."""
        return self.logs.copy()


def retry(max_attempts: int = 3, delay: float = 0.1) -> Callable:
    """Decorator to retry failed function calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    asyncio.run(asyncio.sleep(delay))
        return wrapper
    return decorator


@retry(max_attempts=3)
def unreliable_operation() -> str:
    """Operation that might fail (for demo)."""
    return "success"
