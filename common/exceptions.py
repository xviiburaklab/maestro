from fastapi import HTTPException, status

class BaseServiceException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class AuthException(BaseServiceException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class NotFoundException(BaseServiceException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class ConflictException(BaseServiceException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)
