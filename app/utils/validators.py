"""
Validation utilities for FlowDeck application
"""
import re


# List of commonly used weak passwords
COMMON_PASSWORDS = {
    'password', 'password123', '12345678', '123456789', '1234567890',
    'qwerty', 'abc123', 'monkey', '1234567', '123456',
    '111111', '123123', 'password1', 'qwerty123', 'welcome',
    'admin', 'letmein', 'login', 'passw0rd', 'Pass1234',
    'dragon', 'master', 'hello', 'sunshine', 'princess',
    'football', 'iloveyou', 'welcome1', 'admin123', 'root',
    '12341234', 'password!', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
    '00000000', '11111111', '22222222', '88888888', '99999999',
    'abc12345', 'password12', 'test123', 'user1234', 'demo1234'
}


def validate_password_strength(password):
    """
    Validate password strength according to security best practices.
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    - Not a commonly used password
    
    Args:
        password (str): The password to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password:
        return False, "Password is required."
    
    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    # Check maximum length (prevent DoS attacks)
    if len(password) > 128:
        return False, "Password must not exceed 128 characters."
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/;\'`~]', password):
        return False, r"Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>_-+=[]\/;'`~)."
    
    # Check if password is in common passwords list (case-insensitive)
    if password.lower() in COMMON_PASSWORDS:
        return False, "This password is too common. Please choose a more secure password."
    
    # Check for sequential patterns (like '12345' or 'abcde')
    if has_sequential_pattern(password):
        return False, "Password contains sequential patterns. Please choose a more complex password."
    
    # Check for repeated characters (like '1111' or 'aaaa')
    if has_repeated_characters(password):
        return False, "Password contains too many repeated characters. Please choose a more varied password."
    
    return True, None


def has_sequential_pattern(password, min_length=4):
    """
    Check if password contains sequential characters (numbers or letters).
    
    Args:
        password (str): The password to check
        min_length (int): Minimum length of sequential pattern to detect
    
    Returns:
        bool: True if sequential pattern found
    """
    password_lower = password.lower()
    
    for i in range(len(password_lower) - min_length + 1):
        # Check for sequential numbers
        if password[i:i+min_length].isdigit():
            chars = [int(c) for c in password[i:i+min_length]]
            if all(chars[j] + 1 == chars[j+1] for j in range(len(chars) - 1)):
                return True
            # Check for reverse sequential
            if all(chars[j] - 1 == chars[j+1] for j in range(len(chars) - 1)):
                return True
        
        # Check for sequential letters
        if password_lower[i:i+min_length].isalpha():
            chars = [ord(c) for c in password_lower[i:i+min_length]]
            if all(chars[j] + 1 == chars[j+1] for j in range(len(chars) - 1)):
                return True
            # Check for reverse sequential
            if all(chars[j] - 1 == chars[j+1] for j in range(len(chars) - 1)):
                return True
    
    return False


def has_repeated_characters(password, max_repeats=3):
    """
    Check if password has too many repeated characters in a row.
    
    Args:
        password (str): The password to check
        max_repeats (int): Maximum allowed repeated characters
    
    Returns:
        bool: True if too many repeated characters found
    """
    count = 1
    for i in range(1, len(password)):
        if password[i] == password[i-1]:
            count += 1
            if count > max_repeats:
                return True
        else:
            count = 1
    
    return False


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): The email to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not email:
        return False, "Email is required."
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format."
    
    if len(email) > 254:  # RFC 5321
        return False, "Email address is too long."
    
    return True, None


def validate_username(username):
    """
    Validate username format.
    
    Args:
        username (str): The username to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not username:
        return False, "Username is required."
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters."
    
    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    
    return True, None
