# routes package initializer

# Cho phép imports rõ ràng
from .index import index_bp
from .analyze import analyze_bp

__all__ = ['index_bp', 'analyze_bp']
