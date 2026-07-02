"""
Base service class for common patterns and utilities.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceBase:
    """
    Base service class providing common utility methods and patterns.
    
    All service classes should inherit from this to ensure consistency
    in error handling, logging, and response formatting.
    """
    
    @staticmethod
    def log_operation(operation: str, details: Dict[str, Any] = None, level: str = 'info') -> None:
        """
        Log service operations for audit trails and debugging.
        
        Args:
            operation: Description of the operation being performed
            details: Additional context details to include in the log
            level: Logging level ('info', 'warning', 'error', 'debug')
        """
        log_func = getattr(logger, level, logger.info)
        if details:
            log_func(f"{operation} | Details: {details}")
        else:
            log_func(operation)
    
    @staticmethod
    def format_response(success: bool, data: Any = None, message: str = '', errors: Dict = None) -> Dict:
        """
        Format service response in a consistent structure.
        
        Args:
            success: Whether the operation was successful
            data: Response data payload
            message: Human-readable message
            errors: Dictionary of validation or operation errors
            
        Returns:
            Formatted response dictionary
        """
        return {
            'success': success,
            'message': message,
            'data': data,
            'errors': errors or {}
        }
    
    @staticmethod
    def is_valid_id(value: Any) -> bool:
        """
        Check if a value is a valid database ID (positive integer).
        
        Args:
            value: Value to validate
            
        Returns:
            True if value is a valid ID, False otherwise
        """
        try:
            return isinstance(value, int) and value > 0 or (isinstance(value, str) and int(value) > 0)
        except (ValueError, TypeError):
            return False
