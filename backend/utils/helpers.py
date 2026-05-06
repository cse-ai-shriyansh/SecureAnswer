"""
Utility functions
"""

def format_response(data, status: str = "success"):
    """Format API response"""
    return {
        "status": status,
        "data": data
    }

def handle_error(error_message: str, status_code: int = 400):
    """Handle error responses"""
    return {
        "status": "error",
        "message": error_message,
        "code": status_code
    }
