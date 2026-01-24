"""
Rate limiter configuration module.
Separates limiter initialization to avoid circular imports.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

__all__ = ['limiter']
