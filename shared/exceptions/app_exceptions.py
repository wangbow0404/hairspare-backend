"""
커스텀 예외 클래스
"""

from typing import Optional


class AppException(Exception):
    """
    애플리케이션 커스텀 예외 기본 클래스
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class AuthenticationException(AppException):
    """
    인증 오류
    """
    def __init__(self, message: str = "인증이 필요합니다", code: Optional[str] = None):
        super().__init__(message, status_code=401, code=code or "UNAUTHORIZED")


class AuthorizationException(AppException):
    """
    권한 오류
    """
    def __init__(self, message: str = "권한이 없습니다", code: Optional[str] = None):
        super().__init__(message, status_code=403, code=code or "FORBIDDEN")


class NotFoundException(AppException):
    """
    리소스를 찾을 수 없음
    """
    def __init__(self, message: str = "리소스를 찾을 수 없습니다", code: Optional[str] = None):
        super().__init__(message, status_code=404, code=code or "NOT_FOUND")


class ValidationException(AppException):
    """
    검증 오류
    """
    def __init__(self, message: str = "입력값이 유효하지 않습니다", code: Optional[str] = None):
        super().__init__(message, status_code=422, code=code or "VALIDATION_ERROR")


class ConflictException(AppException):
    """
    충돌 오류 (예: 중복된 리소스)
    """
    def __init__(self, message: str = "리소스가 이미 존재합니다", code: Optional[str] = None):
        super().__init__(message, status_code=409, code=code or "CONFLICT")
