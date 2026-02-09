"""
서비스 프록시 라우트
각 서비스로 요청을 전달
"""

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import Response
import httpx
from typing import Dict
from ..config import SERVICE_URLS
import json

router = APIRouter()


async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    method: str = None
) -> Response:
    """
    서비스로 요청 프록시
    
    Args:
        service_name: 서비스 이름 (auth, job, schedule 등)
        path: 요청 경로
        request: FastAPI Request 객체
        method: HTTP 메서드 (None이면 request.method 사용)
    """
    # 서비스 URL 확인
    if service_name not in SERVICE_URLS:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"서비스를 찾을 수 없습니다: {service_name}"
        )
    
    service_url = SERVICE_URLS[service_name]
    method = method or request.method
    
    # 전체 URL 구성
    full_url = f"{service_url}{path}"
    
    # 요청 본문 읽기
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except Exception:
            pass
    
    # 헤더 준비 (Authorization 헤더는 그대로 전달)
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ["host", "content-length"]:
            headers[key] = value
    
    # 쿼리 파라미터
    query_params = dict(request.query_params)
    
    try:
        # httpx를 사용하여 서비스로 요청 전달
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=full_url,
                headers=headers,
                params=query_params,
                content=body,
            )
            
            # 응답 본문 읽기
            response_body = response.content
            
            # 응답 헤더 준비 (CORS 관련 헤더 제외)
            response_headers = {}
            for key, value in response.headers.items():
                if key.lower() not in ["content-encoding", "content-length", "transfer-encoding"]:
                    response_headers[key] = value
            
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type", "application/json")
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="서비스 응답 시간이 초과되었습니다"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"서비스에 연결할 수 없습니다: {service_name}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"게이트웨이 오류: {str(e)}"
        )


# Auth Service 라우트
@router.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_auth(path: str, request: Request):
    return await proxy_request("auth", f"/api/auth/{path}", request)


# Job Service 라우트
@router.api_route("/api/jobs/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_jobs(path: str, request: Request):
    return await proxy_request("job", f"/api/jobs/{path}", request)


@router.api_route("/api/jobs", methods=["GET", "POST", "OPTIONS"])
async def proxy_jobs_list(request: Request):
    return await proxy_request("job", "/api/jobs", request)


@router.api_route("/api/applications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_applications(path: str, request: Request):
    return await proxy_request("job", f"/api/applications/{path}", request)


@router.api_route("/api/applications", methods=["GET", "POST", "OPTIONS"])
async def proxy_applications_list(request: Request):
    return await proxy_request("job", "/api/applications", request)


# Schedule Service 라우트
@router.api_route("/api/schedules/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_schedules(path: str, request: Request):
    return await proxy_request("schedule", f"/api/schedules/{path}", request)


@router.api_route("/api/schedules", methods=["GET", "POST", "OPTIONS"])
async def proxy_schedules_list(request: Request):
    return await proxy_request("schedule", "/api/schedules", request)


# Chat Service 라우트
@router.api_route("/api/chats/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_chats(path: str, request: Request):
    return await proxy_request("chat", f"/api/chats/{path}", request)


@router.api_route("/api/chats", methods=["GET", "POST", "OPTIONS"])
async def proxy_chats_list(request: Request):
    return await proxy_request("chat", "/api/chats", request)


@router.api_route("/api/messages/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_messages(path: str, request: Request):
    return await proxy_request("chat", f"/api/messages/{path}", request)


@router.api_route("/api/messages", methods=["GET", "POST", "OPTIONS"])
async def proxy_messages_list(request: Request):
    return await proxy_request("chat", "/api/messages", request)


# Energy Service 라우트
@router.api_route("/api/energy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_energy(path: str, request: Request):
    return await proxy_request("energy", f"/api/energy/{path}", request)


# Store Service 라우트
@router.api_route("/api/store/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_store_products(path: str, request: Request):
    return await proxy_request("store", f"/api/store/products/{path}", request)


@router.api_route("/api/store/products", methods=["GET", "POST", "OPTIONS"])
async def proxy_store_products_list(request: Request):
    return await proxy_request("store", "/api/store/products", request)


@router.api_route("/api/store/categories/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_store_categories(path: str, request: Request):
    return await proxy_request("store", f"/api/store/categories/{path}", request)


@router.api_route("/api/store/categories", methods=["GET", "POST", "OPTIONS"])
async def proxy_store_categories_list(request: Request):
    return await proxy_request("store", "/api/store/categories", request)


# Cart Service 라우트
@router.api_route("/api/store/cart/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_cart(path: str, request: Request):
    return await proxy_request("cart", f"/api/store/cart/{path}", request)


@router.api_route("/api/store/cart", methods=["GET", "DELETE", "OPTIONS"])
async def proxy_cart_list(request: Request):
    return await proxy_request("cart", "/api/store/cart", request)


# Order Service 라우트
@router.api_route("/api/store/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_orders(path: str, request: Request):
    return await proxy_request("order", f"/api/store/orders/{path}", request)


@router.api_route("/api/store/orders", methods=["GET", "POST", "OPTIONS"])
async def proxy_orders_list(request: Request):
    return await proxy_request("order", "/api/store/orders", request)


# Payment Service 라우트
@router.api_route("/api/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_payments(path: str, request: Request):
    return await proxy_request("payment", f"/api/payments/{path}", request)


@router.api_route("/api/payments", methods=["GET", "POST", "OPTIONS"])
async def proxy_payments_list(request: Request):
    return await proxy_request("payment", "/api/payments", request)


# Notification Service 라우트
@router.api_route("/api/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_notifications(path: str, request: Request):
    return await proxy_request("notification", f"/api/notifications/{path}", request)


@router.api_route("/api/notifications", methods=["GET", "POST", "OPTIONS"])
async def proxy_notifications_list(request: Request):
    return await proxy_request("notification", "/api/notifications", request)


# Health check
@router.get("/health")
async def health_check():
    """
    API Gateway 헬스 체크
    """
    return {"status": "ok", "service": "api-gateway"}
