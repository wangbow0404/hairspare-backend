"""
공통 응답 형식
Next.js와 호환되는 응답 구조
"""

from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


def success_response(data: Any, status_code: int = 200) -> JSONResponse:
    """
    성공 응답 생성
    
    Args:
        data: 응답 데이터
        status_code: HTTP 상태 코드
    
    Returns:
        JSONResponse 객체
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None
        }
    )


def error_response(
    message: str,
    code: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    에러 응답 생성
    
    Args:
        message: 에러 메시지
        code: 에러 코드 (선택사항)
        status_code: HTTP 상태 코드
    
    Returns:
        JSONResponse 객체
    """
    error_dict: Dict[str, Any] = {
        "message": message
    }
    
    if code:
        error_dict["code"] = code
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": error_dict
        }
    )


def create_error_dict(message: str, code: Optional[str] = None) -> Dict[str, Any]:
    """
    에러 딕셔너리 생성 (JSONResponse가 아닌 딕셔너리 반환)
    """
    error_dict: Dict[str, Any] = {
        "message": message
    }
    
    if code:
        error_dict["code"] = code
    
    return {
        "success": False,
        "data": None,
        "error": error_dict
    }
