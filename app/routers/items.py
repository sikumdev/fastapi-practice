# app/routers/items.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/items/{item_id}")
# {item_id} : 중괄호로 감싼 부분이 경로 파라미터 자리표시자
# URL /items/42 → item_id = 42 으로 함수에 전달됨

async def get_item(item_id: int):
# item_id: int : 타입 힌트 int → FastAPI가 문자열→정수 자동 변환 + 실패 시 422
    return {"item_id": item_id}
    # GET /items/42  → {"item_id": 42}     ✅ (문자열 "42" → 정수 42 자동 변환)
    # GET /items/abc → 422 자동 반환       ❌ (정수 변환 불가)
    # GET /items/3.5 → 422 자동 반환       ❌ (float은 int가 아님)

# 경로 파라미터 여러 개 사용 
@router.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    # URL: /users/7/posts/42 → user_id=7, post_id=42
    # 파라미터 이름이 URL 자리표시자 이름과 반드시 일치해야 함
    return {"user_id": user_id, "post_id": post_id}