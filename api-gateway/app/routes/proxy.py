"""
서비스 프록시 라우트
각 서비스로 요청을 전달
"""

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
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
# 로그인 엔드포인트는 mock 응답 제공 (임시)
@router.api_route("/api/auth/login", methods=["POST", "OPTIONS"])
async def proxy_auth_login(request: Request):
    """
    로그인 (임시 - mock 응답)
    TODO: 실제 auth-service로 프록시
    """
    from fastapi.responses import JSONResponse
    
    # 요청 본문 읽기
    try:
        body = await request.json()
        username = body.get("username", "")
        password = body.get("password", "")
        role = body.get("role", "spare")
    except:
        username = ""
        password = ""
        role = "spare"
    
    # Mock 로그인 응답 (임시로 항상 성공)
    # 실제로는 auth-service에서 검증해야 함
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYTcxYTBlMS04ZDFlLTQ3NjItOGI5NC02YTY2ZTY4ZjIxODYiLCJ1c2VyX2lkIjoiZGE3MWEwZTEtOGQxZS00NzYyLThiOTQtNmE2NmU2OGYyMTg2IiwidXNlcm5hbWUiOiJ0ZXN0MDAxIiwicm9sZSI6InNwYXJlIiwiZXhwIjoxNzcwOTYzODI3LCJpYXQiOjE3NzA4Nzc0Mjd9._Pnj7zJ8cJrTaavmt6wR2LOV57ZPbzsrP7pF1AoRehk"
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "token": mock_token,
                "user": {
                    "id": "da71a0e1-8d1e-4762-8b94-6a66e68f2186",
                    "username": username or "test001",
                    "role": role,
                    "name": "테스트 사용자",
                }
            }
        }
    )


@router.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_auth(path: str, request: Request):
    # login은 위에서 처리되므로 다른 경로만 프록시
    if path == "login":
        return await proxy_auth_login(request)
    return await proxy_request("auth", f"/api/auth/{path}", request)


# Job Service 라우트
@router.api_route("/api/jobs/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_jobs(path: str, request: Request):
    return await proxy_request("job", f"/api/jobs/{path}", request)


@router.api_route("/api/jobs", methods=["GET", "POST", "OPTIONS"])
async def proxy_jobs_list(request: Request):
    try:
        return await proxy_request("job", "/api/jobs", request)
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            return JSONResponse(content={"jobs": []}, status_code=200)
        raise


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
    try:
        return await proxy_request("schedule", "/api/schedules", request)
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE and request.method == "GET":
            return JSONResponse(content={"schedules": []}, status_code=200)
        raise


@router.api_route("/api/work-check/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_work_check(path: str, request: Request):
    try:
        return await proxy_request("schedule", f"/api/work-check/{path}", request)
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            if path.strip("/") == "shop-stats":
                return JSONResponse(
                    content={
                        "data": {
                            "totalCompleted": 0,
                            "vipLevel": "bronze",
                            "tier": "bronze",
                            "thumbsUpReceived": 0,
                            "nextCount": 10,
                            "progress": 0,
                        }
                    },
                    status_code=200,
                )
            return JSONResponse(content={"data": {"consecutiveDays": 0, "energyFromWork": 0}}, status_code=200)
        raise


@router.api_route("/api/work-check", methods=["GET", "POST", "OPTIONS"])
async def proxy_work_check_list(request: Request):
    try:
        return await proxy_request("schedule", "/api/work-check", request)
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            return JSONResponse(content={"consecutiveDays": 0, "energyFromWork": 0}, status_code=200)
        raise


# Chat Service 라우트
@router.api_route("/api/chats/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_chats(path: str, request: Request):
    return await proxy_request("chat", f"/api/chats/{path}", request)


@router.api_route("/api/chats", methods=["GET", "POST", "OPTIONS"])
async def proxy_chats_list(request: Request):
    try:
        return await proxy_request("chat", "/api/chats", request)
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            return JSONResponse(content={"chats": []}, status_code=200)
        raise


@router.api_route("/api/messages/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_messages(path: str, request: Request):
    return await proxy_request("chat", f"/api/messages/{path}", request)


@router.api_route("/api/messages", methods=["GET", "POST", "OPTIONS"])
async def proxy_messages_list(request: Request):
    return await proxy_request("chat", "/api/messages", request)


# Favorites API (아직 전용 서비스 없음 - 빈 목록 반환)
@router.api_route("/api/favorites/check", methods=["POST", "OPTIONS"])
async def proxy_favorites_check(request: Request):
    if request.method == "OPTIONS":
        return Response(status_code=204)
    try:
        body = await request.json()
        job_ids = body.get("jobIds", [])
        return JSONResponse(content={"favorites": {jid: False for jid in job_ids}})
    except Exception:
        return JSONResponse(content={"favorites": {}})


@router.api_route("/api/favorites", methods=["GET", "POST", "DELETE", "OPTIONS"])
async def proxy_favorites(request: Request):
    if request.method == "OPTIONS":
        return Response(status_code=204)
    if request.method == "GET":
        return JSONResponse(content={"favorites": []})
    if request.method == "POST":
        return JSONResponse(content={"success": True}, status_code=201)
    if request.method == "DELETE":
        return Response(status_code=204)
    return Response(status_code=405)


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


# Notification Service 라우트 (임시 - mock 데이터 반환)
# 주의: 더 구체적인 경로가 와일드카드 경로보다 먼저 와야 함
@router.api_route("/api/notifications", methods=["GET", "POST", "OPTIONS"])
async def proxy_notifications_list(request: Request):
    """
    알림 목록 조회 (임시 - mock 데이터)
    TODO: 실제 notification-service로 프록시
    """
    from fastapi.responses import JSONResponse
    from datetime import datetime, timedelta
    
    # Mock 알림 데이터 (Shop 역할용)
    mock_notifications = [
        {
            "id": "notif-1",
            "type": "spare_application",
            "title": "새로운 지원자가 있습니다",
            "message": "김스페어님이 공고에 지원했습니다",
            "isRead": False,
            "createdAt": (datetime.now() - timedelta(minutes=5)).isoformat() + "Z",
            "relatedJobId": "job-1",
            "relatedUserId": "spare-1",
        },
        {
            "id": "notif-2",
            "type": "schedule_confirmed",
            "title": "스케줄이 확정되었습니다",
            "message": "2026년 2월 12일 오후 2시 스케줄이 확정되었습니다",
            "isRead": False,
            "createdAt": (datetime.now() - timedelta(hours=1)).isoformat() + "Z",
            "relatedJobId": "job-2",
            "relatedUserId": "spare-2",
            "scheduleDate": "2026-02-12",
            "scheduleTime": "14:00",
        },
        {
            "id": "notif-3",
            "type": "booking_request",
            "title": "공간 예약 요청",
            "message": "이디자이너님이 공간 예약을 요청했습니다",
            "isRead": True,
            "createdAt": (datetime.now() - timedelta(hours=3)).isoformat() + "Z",
            "relatedUserId": "spare-2",
        },
        {
            "id": "notif-4",
            "type": "schedule_cancelled",
            "title": "스케줄이 취소되었습니다",
            "message": "2026년 2월 11일 오전 10시 스케줄이 취소되었습니다",
            "isRead": True,
            "createdAt": (datetime.now() - timedelta(days=1)).isoformat() + "Z",
            "relatedJobId": "job-3",
            "relatedUserId": "spare-3",
            "scheduleDate": "2026-02-11",
            "scheduleTime": "10:00",
        },
    ]
    
    # 쿼리 파라미터 파싱
    query_params = dict(request.query_params)
    unread_only = query_params.get("unreadOnly", "false").lower() == "true"
    
    filtered_notifications = mock_notifications.copy()
    if (unread_only):
        filtered_notifications = [n for n in filtered_notifications if not n["isRead"]]
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "notifications": filtered_notifications,
                "total": len(filtered_notifications),
                "unreadCount": len([n for n in filtered_notifications if not n["isRead"]]),
            }
        }
    )


@router.api_route("/api/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_notifications(path: str, request: Request):
    """
    알림 상세/수정/삭제 (임시 - mock 응답)
    TODO: 실제 notification-service로 프록시
    """
    from fastapi.responses import JSONResponse
    
    if request.method == "PUT" and path.endswith("/read"):
        # 읽음 처리
        notification_id = path.replace("/read", "")
        return JSONResponse(
            content={
                "success": True,
                "message": "알림이 읽음 처리되었습니다",
            }
        )
    elif request.method == "DELETE":
        # 삭제 처리
        return JSONResponse(
            content={
                "success": True,
                "message": "알림이 삭제되었습니다",
            }
        )
    else:
        # 기본적으로 notification-service로 프록시 시도
        return await proxy_request("notification", f"/api/notifications/{path}", request)


# Spares Service 라우트 (임시 - mock 데이터 반환)
# 주의: 더 구체적인 경로가 와일드카드 경로보다 먼저 와야 함
@router.api_route("/api/spares", methods=["GET", "OPTIONS"])
async def proxy_spares_list(request: Request):
    """
    스페어 목록 조회 (임시 - mock 데이터)
    TODO: 실제 spare-service로 프록시하거나 auth-service에서 role='spare'인 User 목록 가져오기
    """
    from fastapi.responses import JSONResponse
    
    # Mock 스페어 데이터
    mock_spares = [
        {
            "id": "spare-1",
            "name": "김스페어",
            "role": "step",
            "regionId": "seoul-gangnam",
            "experience": 5,
            "rating": 4.8,
            "reviewCount": 32,
            "thumbsUpCount": 28,
            "specialties": ["컷트", "펌", "염색"],
            "availableTimes": ["오전", "오후"],
            "hourlyRate": 25000,
            "isVerified": True,
            "isLicenseVerified": True,
            "noShowCount": 0,
            "completedJobs": 45,
            "createdAt": "2023-01-15T00:00:00Z",
            "lastActiveAt": "2026-01-25T10:30:00Z",
        },
        {
            "id": "spare-2",
            "name": "이디자이너",
            "role": "designer",
            "regionId": "seoul-gangnam",
            "experience": 8,
            "rating": 4.9,
            "reviewCount": 67,
            "thumbsUpCount": 65,
            "specialties": ["컷트", "디자인"],
            "availableTimes": ["오후", "저녁"],
            "hourlyRate": 30000,
            "isVerified": True,
            "isLicenseVerified": True,
            "noShowCount": 0,
            "completedJobs": 89,
            "createdAt": "2022-06-20T00:00:00Z",
            "lastActiveAt": "2026-01-25T09:15:00Z",
        },
        {
            "id": "spare-3",
            "name": "박헤어",
            "role": "step",
            "regionId": "seoul-seocho",
            "experience": 3,
            "rating": 4.5,
            "reviewCount": 18,
            "thumbsUpCount": 15,
            "specialties": ["컷트", "스타일링"],
            "availableTimes": ["오전", "오후", "저녁"],
            "hourlyRate": 20000,
            "isVerified": True,
            "isLicenseVerified": False,
            "noShowCount": 1,
            "completedJobs": 23,
            "createdAt": "2024-03-10T00:00:00Z",
            "lastActiveAt": "2026-01-24T16:20:00Z",
        },
        {
            "id": "spare-4",
            "name": "최미용",
            "role": "step",
            "regionId": "seoul-seocho",
            "experience": 6,
            "rating": 4.7,
            "reviewCount": 41,
            "thumbsUpCount": 38,
            "specialties": ["펌", "염색", "케어"],
            "availableTimes": ["오전", "오후"],
            "hourlyRate": 28000,
            "isVerified": True,
            "isLicenseVerified": True,
            "noShowCount": 0,
            "completedJobs": 56,
            "createdAt": "2023-05-12T00:00:00Z",
            "lastActiveAt": "2026-01-25T11:00:00Z",
        },
        {
            "id": "spare-5",
            "name": "정스타일",
            "role": "step",
            "regionId": "busan-haeundae",
            "experience": 4,
            "rating": 4.6,
            "reviewCount": 29,
            "thumbsUpCount": 26,
            "specialties": ["컷트", "염색"],
            "availableTimes": ["오후", "저녁"],
            "hourlyRate": 22000,
            "isVerified": True,
            "isLicenseVerified": True,
            "noShowCount": 0,
            "completedJobs": 38,
            "createdAt": "2023-09-25T00:00:00Z",
            "lastActiveAt": "2026-01-25T08:45:00Z",
        },
    ]
    
    # 쿼리 파라미터 파싱
    query_params = dict(request.query_params)
    role = query_params.get("role")
    region_ids = query_params.get("regionIds")
    sort_by = query_params.get("sortBy", "popular")
    search_query = query_params.get("search") or query_params.get("searchQuery")
    is_license_verified = query_params.get("isLicenseVerified")
    
    # 필터링
    filtered_spares = mock_spares.copy()
    
    if role:
        filtered_spares = [s for s in filtered_spares if s["role"] == role]
    
    if region_ids:
        # regionIds가 리스트로 전달될 수도 있고, 쉼표로 구분된 문자열로 전달될 수도 있음
        if isinstance(region_ids, list):
            region_list = region_ids
        elif isinstance(region_ids, str):
            # 쉼표로 구분된 문자열 처리
            region_list = [r.strip() for r in region_ids.split(",") if r.strip()]
        else:
            region_list = []
        
        if region_list:
            filtered_spares = [s for s in filtered_spares if s["regionId"] in region_list]
    
    if search_query:
        query = search_query.lower()
        filtered_spares = [
            s for s in filtered_spares
            if query in s["name"].lower() or any(query in spec.lower() for spec in s["specialties"])
        ]
    
    # 면허 인증 필터
    if is_license_verified is not None:
        is_verified = str(is_license_verified).lower() == "true"
        filtered_spares = [s for s in filtered_spares if s["isLicenseVerified"] == is_verified]
    
    # 정렬
    if sort_by == "popular":
        filtered_spares.sort(key=lambda x: x["thumbsUpCount"] * x["completedJobs"], reverse=True)
    elif sort_by == "newest":
        filtered_spares.sort(key=lambda x: x["createdAt"], reverse=True)
    elif sort_by == "experience":
        filtered_spares.sort(key=lambda x: x["experience"], reverse=True)
    elif sort_by == "completed":
        filtered_spares.sort(key=lambda x: x["completedJobs"], reverse=True)
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "spares": filtered_spares,
                "total": len(filtered_spares),
            }
        }
    )


# Space Rentals Service 라우트 (임시 - mock 데이터 반환)
# 주의: 더 구체적인 경로가 와일드카드 경로보다 먼저 와야 함

# 내 공간 목록 조회 - 가장 구체적인 경로를 먼저 등록
@router.get("/api/space-rentals/my-spaces")
@router.options("/api/space-rentals/my-spaces")
async def proxy_my_spaces(request: Request):
    """
    내가 등록한 공간 목록 조회 (임시 - mock 데이터)
    TODO: 실제 space-rental-service로 프록시
    """
    from fastapi.responses import JSONResponse
    
    # Mock 공간 데이터
    mock_spaces = [
        {
            "id": "space-1",
            "shopId": "shop-1",
            "shopName": "테스트 미용실",
            "address": "서울시 강남구 테헤란로 123",
            "detailAddress": "4층",
            "regionId": "seoul-gangnam",
            "pricePerHour": 50000,
            "facilities": ["의자", "거울", "세면대"],
            "imageUrls": [],
            "description": "깔끔한 미용실 공간입니다",
            "status": "active",
            "createdAt": "2026-01-15T00:00:00Z",
            "updatedAt": "2026-01-15T00:00:00Z",
        },
        {
            "id": "space-2",
            "shopId": "shop-1",
            "shopName": "테스트 미용실",
            "address": "서울시 서초구 서초대로 456",
            "detailAddress": "2층",
            "regionId": "seoul-seocho",
            "pricePerHour": 45000,
            "facilities": ["의자", "세트", "샴푸대", "드라이어"],
            "imageUrls": [],
            "description": "넓고 쾌적한 공간입니다",
            "status": "active",
            "createdAt": "2026-01-20T00:00:00Z",
            "updatedAt": "2026-01-20T00:00:00Z",
        }
    ]
    
    query_params = dict(request.query_params)
    status_filter = query_params.get("status")
    
    filtered_spaces = mock_spaces.copy()
    if status_filter:
        filtered_spaces = [s for s in filtered_spaces if s["status"] == status_filter]
    
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "rentals": filtered_spaces,
                "total": len(filtered_spaces),
            }
        }
    )


# 공간 목록 조회
@router.api_route("/api/space-rentals", methods=["GET", "POST", "OPTIONS"])
async def proxy_space_rentals_list(request: Request):
    """
    공간 목록 조회 (임시)
    TODO: 실제 space-rental-service로 프록시
    """
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "rentals": [],
                "total": 0,
            }
        }
    )


# 공간대여 와일드카드 라우트 - 가장 마지막에 등록
@router.api_route("/api/space-rentals/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_space_rentals(path: str, request: Request):
    """
    공간대여 관련 엔드포인트 (임시)
    TODO: 실제 space-rental-service로 프록시
    """
    from fastapi.responses import JSONResponse
    
    # my-spaces 경로는 이미 위에서 처리되므로 여기서는 다른 경로만 처리
    if path == "my-spaces":
        # 이 경우는 발생하지 않아야 하지만, 안전을 위해 처리
        return await proxy_my_spaces(request)
    
    return JSONResponse(
        content={
            "success": False,
            "message": "공간대여 서비스는 아직 구현되지 않았습니다",
        },
        status_code=501
    )


# Spares 상세 조회 (더 구체적인 경로는 나중에)
@router.api_route("/api/spares/{path:path}", methods=["GET", "OPTIONS"])
async def proxy_spares_detail(path: str, request: Request):
    """
    스페어 상세 조회 (임시 - mock 데이터)
    """
    # TODO: 실제 spare-service로 프록시하거나 auth-service에서 User 정보 가져오기
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "id": path,
                "name": "임시 스페어",
                "role": "step",
                "regionId": "seoul-gangnam",
                "experience": 5,
                "rating": 4.8,
                "reviewCount": 32,
                "thumbsUpCount": 28,
                "specialties": ["컷트", "펌", "염색"],
                "availableTimes": ["오전", "오후"],
                "hourlyRate": 25000,
                "isVerified": True,
                "isLicenseVerified": True,
                "noShowCount": 0,
                "completedJobs": 45,
                "createdAt": "2023-01-15T00:00:00Z",
                "lastActiveAt": "2026-01-25T10:30:00Z",
            }
        }
    )


# Admin Service 라우트
# Python FastAPI에서 직접 데이터베이스에 연결하여 통계 조회

# 관리자 대시보드 통계
@router.api_route("/api/admin/stats", methods=["GET", "OPTIONS"])
async def proxy_admin_stats(request: Request):
    """
    관리자 대시보드 통계 조회
    raw SQL을 사용하여 모델 import 없이 직접 DB 조회
    """
    from fastapi.responses import JSONResponse
    from sqlalchemy import text
    from datetime import datetime
    import sys
    import os

    # shared 라이브러리 경로 추가
    current_file = os.path.abspath(__file__)
    backend_dir = os.path.abspath(os.path.join(current_file, "../../../"))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    try:
        from shared.database.session import SessionLocal

        db = SessionLocal()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        def _scalar(stmt, params=None, default=0):
            try:
                r = db.execute(text(stmt), params or {})
                val = r.scalar()
                return val if val is not None else default
            except Exception as e:
                print(f"[Admin Stats] Query error: {e}")
                return default

        def _scalar_try(*queries):
            """여러 쿼리를 시도하여 첫 성공 결과 반환"""
            for stmt, params in queries:
                try:
                    r = db.execute(text(stmt), params or {})
                    val = r.scalar()
                    if val is not None:
                        return val
                except Exception:
                    continue
            return 0

        # User 통계 (createdAt 또는 created_at 컬럼 지원)
        total_users = _scalar('SELECT COUNT(*) FROM "User"')
        today_users = _scalar_try(
            ('SELECT COUNT(*) FROM "User" WHERE "createdAt" >= :today', {"today": today_start}),
            ('SELECT COUNT(*) FROM "User" WHERE "created_at" >= :today', {"today": today_start}),
        )
        try:
            r = db.execute(text('SELECT role, COUNT(*) FROM "User" GROUP BY role'))
            by_role = {row[0]: row[1] for row in r.fetchall()}
        except Exception:
            by_role = {}

        # Job, Schedule, Energy 통계
        total_jobs = _scalar('SELECT COUNT(*) FROM "Job"')
        active_jobs = _scalar('SELECT COUNT(*) FROM "Job" WHERE status = \'published\'')

        today_payments = 0
        total_payments = 0

        today_schedules = _scalar_try(
            ('SELECT COUNT(*) FROM "Schedule" WHERE "checkInTime" >= :today', {"today": today_start}),
            ('SELECT COUNT(*) FROM "Schedule" WHERE "check_in_time" >= :today', {"today": today_start}),
        )
        total_schedules = _scalar('SELECT COUNT(*) FROM "Schedule"')

        energy_wallets = _scalar('SELECT COUNT(*) FROM "EnergyWallet"')
        total_energy_transactions = _scalar('SELECT COUNT(*) FROM "EnergyTransaction"')
        no_show_count = _scalar('SELECT COUNT(*) FROM "NoShowHistory"')

        stats = {
            "users": {"total": total_users, "today": today_users, "byRole": by_role},
            "jobs": {"total": total_jobs, "active": active_jobs},
            "payments": {"today": today_payments, "total": total_payments},
            "schedules": {"today": today_schedules, "total": total_schedules},
            "energy": {"wallets": energy_wallets, "transactions": total_energy_transactions},
            "noShow": {"total": no_show_count},
        }

        db.close()
        return JSONResponse(content={"stats": stats})

    except ImportError as e:
        import traceback
        print(f"[Admin Stats Import Error] {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모듈 로드 실패: {str(e)}",
        )
    except Exception as e:
        import traceback
        print(f"[Admin Stats Error] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 실패: {str(e)}",
        )


# 관리자 최근 활동
@router.api_route("/api/admin/activities", methods=["GET", "OPTIONS"])
async def proxy_admin_activities(request: Request):
    """
    관리자 최근 활동 목록 (회원가입, 공고등록, 결제완료, 노쇼신고, 에너지충전 등)
    """
    from fastapi.responses import JSONResponse
    from datetime import datetime, timedelta

    # Mock 최근 활동 (실제로는 DB에서 User, Job, Payment 등 조회하여 병합)
    activities = [
        {"type": "signup", "label": "회원가입", "entity": "김디자이너", "ago": "5분 전", "color": "blue"},
        {"type": "job", "label": "공고등록", "entity": "이미용실", "ago": "12분 전", "color": "purple"},
        {"type": "payment", "label": "결제완료", "entity": "박스텝", "ago": "23분 전", "color": "green"},
        {"type": "noshow", "label": "노쇼신고", "entity": "최사장", "ago": "1시간 전", "color": "red"},
        {"type": "energy", "label": "에너지충전", "entity": "정디자이너", "ago": "2시간 전", "color": "yellow"},
    ]
    return JSONResponse(content={"activities": activities})


# 관리자 회원 목록
@router.api_route("/api/admin/users", methods=["GET", "OPTIONS"])
async def proxy_admin_users(request: Request):
    """
    관리자 회원 목록 조회
    DB에서 직접 조회 (stats와 동일한 데이터 소스) 또는 mock 데이터 반환
    """
    from fastapi.responses import JSONResponse
    from sqlalchemy import text
    from datetime import datetime, timedelta
    import sys
    import os

    query_params = dict(request.query_params)
    page = int(query_params.get("page", 1))
    limit = int(query_params.get("limit", 20))
    role = query_params.get("role")
    search = query_params.get("search")
    signupMethod = query_params.get("signupMethod")

    # DB에서 직접 조회 (stats와 동일)
    try:
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.abspath(os.path.join(current_file, "../../../"))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from shared.database.session import SessionLocal

        db = SessionLocal()
        try:
            # User 테이블 조회 - created_at/createdAt 둘 다 시도
            for created_col in ['created_at', '"createdAt"']:
                try:
                    base_sql = f'SELECT id, username, email, name, phone, role, {created_col} FROM "User" WHERE 1=1'
                    count_sql = 'SELECT COUNT(*) FROM "User" WHERE 1=1'
                    params = {}
                    conditions = []

                    if role:
                        conditions.append('role = :role')
                        params['role'] = role
                    if search:
                        conditions.append('(name ILIKE :search OR email ILIKE :search OR phone::text LIKE :search)')
                        params['search'] = f'%{search.lower()}%'

                    where_clause = ' AND '.join(conditions) if conditions else '1=1'
                    full_count_sql = count_sql.replace('WHERE 1=1', f'WHERE {where_clause}')
                    full_list_sql = base_sql.replace('WHERE 1=1', f'WHERE {where_clause}')
                    full_list_sql += f' ORDER BY {created_col} DESC LIMIT :limit OFFSET :offset'
                    params['limit'] = limit
                    params['offset'] = (page - 1) * limit

                    total = db.execute(text(full_count_sql), params).scalar() or 0
                    rows = db.execute(text(full_list_sql), params).fetchall()

                    users = []
                    for row in rows:
                        created_at = row[6] if len(row) > 6 else None
                        created_str = (created_at.isoformat() + 'Z') if hasattr(created_at, 'isoformat') else str(created_at or '')
                        users.append({
                            "id": str(row[0]),
                            "email": row[2] or "",
                            "name": (row[3] or row[1] or "이름 없음") if len(row) > 3 else "이름 없음",
                            "role": row[5] or "spare" if len(row) > 5 else "spare",
                            "phone": (row[4] or "") if len(row) > 4 else "",
                            "createdAt": created_str,
                            "accounts": [{"provider": "email"}],
                            "energyWallet": {"balance": 0},
                            "_count": {"jobs": 0, "applications": 0, "schedules": 0},
                        })

                    total_pages = (total + limit - 1) // limit if total > 0 else 1
                    db.close()
                    return JSONResponse(content={
                        "users": users,
                        "pagination": {"page": page, "limit": limit, "total": total, "totalPages": total_pages},
                    })
                except Exception as col_err:
                    continue
            db.close()
            raise Exception("User table column not found")
        except Exception as e:
            db.close()
            raise
    except Exception as db_err:
        # DB 실패 시 mock 데이터 반환
        # Mock 회원 데이터 (각 역할별로 생성)
        all_users = []
        
        # 스페어 회원
        for i in range(1, 81):
            all_users.append({
                "id": f"spare-{i}",
                "email": f"spare{i}@example.com",
                "name": f"스페어{i}",
                "role": "spare",
                "phone": f"010-{1000+i:04d}-{2000+i:04d}",
                "createdAt": (datetime.now() - timedelta(days=i)).isoformat() + "Z",
                "accounts": [{"provider": "email"}] if i % 3 == 0 else [{"provider": "kakao"}] if i % 3 == 1 else [{"provider": "naver"}],
                "energyWallet": {
                    "balance": (i * 10) % 500
                },
                "_count": {
                    "jobs": 0,
                    "applications": i * 2,
                    "schedules": i * 3,
                }
            })
        
        # 미용실 회원
        for i in range(1, 51):
            all_users.append({
                "id": f"shop-{i}",
                "email": f"shop{i}@example.com",
                "name": f"미용실{i}",
                "role": "shop",
                "phone": f"010-{3000+i:04d}-{4000+i:04d}",
                "createdAt": (datetime.now() - timedelta(days=i+10)).isoformat() + "Z",
                "accounts": [{"provider": "email"}] if i % 2 == 0 else [{"provider": "kakao"}],
                "energyWallet": {
                    "balance": (i * 5) % 300
                },
                "_count": {
                    "jobs": i * 2,
                    "applications": 0,
                    "schedules": i * 4,
                }
            })
        
        # 디자이너/판매자 회원
        for i in range(1, 21):
            all_users.append({
                "id": f"seller-{i}",
                "email": f"seller{i}@example.com",
                "name": f"디자이너{i}",
                "role": "seller",
                "phone": f"010-{5000+i:04d}-{6000+i:04d}",
                "createdAt": (datetime.now() - timedelta(days=i+20)).isoformat() + "Z",
                "accounts": [{"provider": "email"}] if i % 2 == 0 else [{"provider": "google"}],
                "energyWallet": {
                    "balance": (i * 8) % 400
                },
                "_count": {
                    "jobs": 0,
                    "applications": 0,
                    "schedules": 0,
                }
            })
        
        # 필터링
        filtered_users = all_users.copy()
        
        if role:
            filtered_users = [u for u in filtered_users if u["role"] == role]
        
        if search:
            search_lower = search.lower()
            filtered_users = [
                u for u in filtered_users
                if search_lower in u["name"].lower()
                or search_lower in u["email"].lower()
                or (u.get("phone") and search_lower in u["phone"])
            ]
        
        if signupMethod and signupMethod != "all":
            filtered_users = [
                u for u in filtered_users
                if u.get("accounts") and len(u["accounts"]) > 0 and u["accounts"][0].get("provider") == signupMethod
            ]
        
        # 페이지네이션
        total = len(filtered_users)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_users = filtered_users[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "users": paginated_users,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                }
            }
        )


# 관리자 회원 상세
@router.api_route("/api/admin/users/{user_id}", methods=["GET", "OPTIONS"])
async def proxy_admin_user_detail(user_id: str, request: Request):
    """
    관리자 회원 상세 조회 (mock 데이터)
    """
    from fastapi.responses import JSONResponse
    
    # Mock 회원 상세 데이터
    mock_user = {
        "id": user_id,
        "email": f"{user_id}@example.com",
        "name": f"회원 {user_id}",
        "role": "spare" if "spare" in user_id else "shop" if "shop" in user_id else "seller",
        "phone": "010-1234-5678",
        "createdAt": "2024-01-01T00:00:00Z",
        "accounts": [{"provider": "email"}],
        "energyWallet": {
            "balance": 100
        },
        "_count": {
            "jobs": 5,
            "applications": 10,
            "schedules": 15,
        }
    }
    
    return JSONResponse(
        content=mock_user
    )


# 관리자 공고 목록
@router.api_route("/api/admin/jobs", methods=["GET", "OPTIONS"])
async def proxy_admin_jobs(request: Request):
    """
    관리자 공고 목록 조회
    Next.js API Routes를 프록시하거나 mock 데이터 반환
    """
    # Next.js 서버가 실행 중이면 프록시, 아니면 mock 데이터 반환
    try:
        return await proxy_request("nextjs", "/api/admin/jobs", request)
    except Exception:
        # Next.js 서버가 없으면 mock 데이터 반환
        from fastapi.responses import JSONResponse
        from datetime import datetime, timedelta
        
        query_params = dict(request.query_params)
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 20))
        status = query_params.get("status")
        isUrgent = query_params.get("isUrgent")
        search = query_params.get("search")
        
        # Mock 공고 데이터
        all_jobs = []
        statuses = ["published", "closed", "completed"]
        
        for i in range(1, 321):
            job_status = statuses[i % 3]
            all_jobs.append({
                "id": f"job-{i}",
                "title": f"공고 제목 {i}",
                "date": (datetime.now() + timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                "time": f"{10 + (i % 10)}:00",
                "amount": 30000 + (i * 1000),
                "energy": 50,
                "requiredCount": 2,
                "isUrgent": i % 5 == 0,
                "isPremium": i % 7 == 0,
                "status": job_status,
                "createdAt": (datetime.now() - timedelta(days=i % 60)).isoformat() + "Z",
                "shop": {
                    "id": f"shop-{(i % 50) + 1}",
                    "name": f"미용실{(i % 50) + 1}",
                    "email": f"shop{(i % 50) + 1}@example.com",
                },
                "region": {
                    "id": f"region-{(i % 10) + 1}",
                    "name": f"서울 강남구" if (i % 10) < 5 else f"서울 서초구",
                },
                "_count": {
                    "applications": i % 10,
                    "schedules": i % 5,
                }
            })
        
        # 필터링
        filtered_jobs = all_jobs.copy()
        
        if status:
            filtered_jobs = [j for j in filtered_jobs if j["status"] == status]
        
        if isUrgent is not None:
            is_urgent_bool = isUrgent.lower() == "true"
            filtered_jobs = [j for j in filtered_jobs if j["isUrgent"] == is_urgent_bool]
        
        if search:
            search_lower = search.lower()
            filtered_jobs = [
                j for j in filtered_jobs
                if search_lower in j["title"].lower()
                or search_lower in j["shop"]["name"].lower()
            ]
        
        # 페이지네이션
        total = len(filtered_jobs)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_jobs = filtered_jobs[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "jobs": paginated_jobs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                }
            }
        )


# 관리자 결제 목록
@router.api_route("/api/admin/payments", methods=["GET", "OPTIONS"])
async def proxy_admin_payments(request: Request):
    """
    관리자 결제 목록 조회
    Next.js API Routes를 프록시하거나 mock 데이터 반환
    """
    # Next.js 서버가 실행 중이면 프록시, 아니면 mock 데이터 반환
    try:
        return await proxy_request("nextjs", "/api/admin/payments", request)
    except Exception:
        # Next.js 서버가 없으면 mock 데이터 반환
        from fastapi.responses import JSONResponse
        from datetime import datetime, timedelta
        
        query_params = dict(request.query_params)
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 20))
        status = query_params.get("status")
        type_filter = query_params.get("type")
        
        # Mock 결제 데이터
        all_payments = []
        statuses = ["success", "pending", "failed", "cancelled"]
        types = ["energy_purchase", "subscription", "premium_fix"]
        
        for i in range(1, 201):
            all_payments.append({
                "id": f"payment-{i}",
                "userId": f"user-{(i % 150) + 1}",
                "orderId": f"ORDER-{i:06d}",
                "type": types[i % 3],
                "amount": 10000 + (i * 1000),
                "status": statuses[i % 4],
                "paymentMethod": "카드" if i % 2 == 0 else "계좌이체",
                "createdAt": (datetime.now() - timedelta(days=i % 90)).isoformat() + "Z",
                "user": {
                    "id": f"user-{(i % 150) + 1}",
                    "name": f"사용자{(i % 150) + 1}",
                    "email": f"user{(i % 150) + 1}@example.com",
                    "role": "spare" if (i % 150) < 80 else "shop" if (i % 150) < 130 else "seller",
                }
            })
        
        # 필터링
        filtered_payments = all_payments.copy()
        
        if status:
            filtered_payments = [p for p in filtered_payments if p["status"] == status]
        
        if type_filter:
            filtered_payments = [p for p in filtered_payments if p["type"] == type_filter]
        
        # 페이지네이션
        total = len(filtered_payments)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_payments = filtered_payments[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "payments": paginated_payments,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                }
            }
        )


# 관리자 에너지 거래 내역
@router.api_route("/api/admin/energy", methods=["GET", "OPTIONS"])
async def proxy_admin_energy(request: Request):
    """
    관리자 에너지 거래 내역 조회
    Next.js API Routes를 프록시하거나 mock 데이터 반환
    """
    # Next.js 서버가 실행 중이면 프록시, 아니면 mock 데이터 반환
    try:
        return await proxy_request("nextjs", "/api/admin/energy", request)
    except Exception:
        # Next.js 서버가 없으면 mock 데이터 반환
        from fastapi.responses import JSONResponse
        from datetime import datetime, timedelta
        
        query_params = dict(request.query_params)
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 20))
        type_filter = query_params.get("type")
        
        # Mock 에너지 거래 데이터
        all_transactions = []
        types = ["purchase", "lock", "return", "forfeit", "reward"]
        states = ["completed", "pending", "failed"]
        
        for i in range(1, 1501):
            transaction_type = types[i % 5]
            amount = 50 if transaction_type == "purchase" else -30 if transaction_type == "lock" else 30 if transaction_type == "return" else -50 if transaction_type == "forfeit" else 100
            
            all_transactions.append({
                "id": f"energy-{i}",
                "walletId": f"wallet-{(i % 200) + 1}",
                "jobId": f"job-{(i % 320) + 1}" if i % 3 == 0 else None,
                "type": transaction_type,
                "amount": amount,
                "state": states[i % 3],
                "description": f"{transaction_type} 거래 {i}",
                "createdAt": (datetime.now() - timedelta(days=i % 180)).isoformat() + "Z",
                "energyWallet": {
                    "user": {
                        "id": f"user-{(i % 150) + 1}",
                        "name": f"사용자{(i % 150) + 1}",
                        "email": f"user{(i % 150) + 1}@example.com",
                        "role": "spare" if (i % 150) < 80 else "shop" if (i % 150) < 130 else "seller",
                    }
                },
                "job": {
                    "id": f"job-{(i % 320) + 1}",
                    "title": f"공고 제목 {(i % 320) + 1}",
                } if i % 3 == 0 else None,
            })
        
        # 필터링
        filtered_transactions = all_transactions.copy()
        
        if type_filter:
            filtered_transactions = [t for t in filtered_transactions if t["type"] == type_filter]
        
        # 페이지네이션
        total = len(filtered_transactions)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_transactions = filtered_transactions[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "transactions": paginated_transactions,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                }
            }
        )


# 관리자 노쇼 이력
@router.api_route("/api/admin/noshow", methods=["GET", "OPTIONS"])
async def proxy_admin_noshow(request: Request):
    """
    관리자 노쇼 이력 조회
    Next.js API Routes를 프록시하거나 mock 데이터 반환
    """
    # Next.js 서버가 실행 중이면 프록시, 아니면 mock 데이터 반환
    try:
        return await proxy_request("nextjs", "/api/admin/noshow", request)
    except Exception:
        # Next.js 서버가 없으면 mock 데이터 반환
        from fastapi.responses import JSONResponse
        from datetime import datetime, timedelta
        
        query_params = dict(request.query_params)
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 20))
        
        # Mock 노쇼 이력 데이터
        all_history = []
        
        for i in range(1, 9):
            all_history.append({
                "id": f"noshow-{i}",
                "noshowDate": (datetime.now() - timedelta(days=i)).isoformat() + "Z",
                "createdAt": (datetime.now() - timedelta(days=i)).isoformat() + "Z",
                "energyWallet": {
                    "user": {
                        "id": f"spare-{i}",
                        "name": f"스페어{i}",
                        "email": f"spare{i}@example.com",
                        "role": "spare",
                    }
                },
                "job": {
                    "id": f"job-{i}",
                    "title": f"공고 제목 {i}",
                    "shop": {
                        "name": f"미용실{i}",
                    }
                }
            })
        
        # 페이지네이션
        total = len(all_history)
        total_pages = (total + limit - 1) // limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_history = all_history[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "history": paginated_history,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": total_pages,
                }
            }
        )


# Health check
@router.get("/health")
async def health_check():
    """
    API Gateway 헬스 체크
    """
    return {"status": "ok", "service": "api-gateway"}
