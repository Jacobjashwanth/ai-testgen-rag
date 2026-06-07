"""
Sample user authentication module for AI Test Generator demonstration.
This module contains functions and classes for user authentication.
"""

import hashlib
import re
from typing import Optional, Dict


class User:
    """Represents a user in the system."""
    
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
    
    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash."""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash


class AuthManager:
    """Manages user authentication and session."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, str] = {}
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Register a new user.
        
        Args:
            username: The username (must be 3-20 chars)
            email: Valid email address
            password: Password (must be 8+ chars)
        
        Returns:
            True if registration successful, False otherwise
        """
        if username in self.users:
            raise ValueError("Username already exists")
        
        if not self._validate_username(username):
            raise ValueError("Username must be 3-20 characters, alphanumeric")
        
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        if not self._validate_password(password):
            raise ValueError("Password must be at least 8 characters")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(username, email, password_hash)
        self.users[username] = user
        return True
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create session.
        
        Args:
            username: The username
            password: The password
        
        Returns:
            Session token if login successful, None otherwise
        """
        if username not in self.users:
            return None
        
        user = self.users[username]
        if not user.is_active:
            return None
        
        if not user.verify_password(password):
            return None
        
        session_token = hashlib.sha256(f"{username}{len(self.sessions)}".encode()).hexdigest()
        self.sessions[session_token] = username
        return session_token
    
    def logout(self, session_token: str) -> bool:
        """
        End user session.
        
        Args:
            session_token: The session token
        
        Returns:
            True if logout successful
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def verify_session(self, session_token: str) -> Optional[str]:
        """
        Verify if session is valid and return username.
        
        Args:
            session_token: The session token
        
        Returns:
            Username if valid, None otherwise
        """
        return self.sessions.get(session_token)
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            username: The username
            old_password: Current password
            new_password: New password
        
        Returns:
            True if password changed successfully
        """
        if username not in self.users:
            return False
        
        user = self.users[username]
        if not user.verify_password(old_password):
            return False
        
        if not self._validate_password(new_password):
            raise ValueError("Password must be at least 8 characters")
        
        user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        return True
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength."""
        return len(password) >= 8


def reset_password(username: str, auth_manager: AuthManager) -> str:
    """
    Generate a temporary password for password reset.
    
    Args:
        username: The username
        auth_manager: The authentication manager instance
    
    Returns:
        Temporary password
    """
    if username not in auth_manager.users:
        raise ValueError("User not found")
    
    temp_password = "TEMP_" + hashlib.sha256(username.encode()).hexdigest()[:16]
    return temp_password


def is_user_active(username: str, auth_manager: AuthManager) -> bool:
    """Check if user account is active."""
    if username not in auth_manager.users:
        return False
    return auth_manager.users[username].is_active
