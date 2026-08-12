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


'''
# ── 쿼리 파라미터 기본 ──────────────────────────────────────────────────────
@router.get("/search")
async def search(keyword: str, limit: int = 10):
# keyword: str      — 기본값 없음 → 필수 쿼리 파라미터
# limit: int = 10   — 기본값 있음 → 선택 쿼리 파라미터 (생략하면 10 사용)

    # GET /search?keyword=AI&limit=5 → keyword="AI", limit=5           ✅
    # GET /search?keyword=AI         → keyword="AI", limit=10 (기본값)  ✅
    # GET /search                    → 422 (keyword 필수, 기본값 없음)   ❌
    # GET /search?keyword=AI&limit=x → 422 (limit이 int가 아님)         ❌
    return {"keyword": keyword, "limit": limit}

# ── bool 타입 쿼리 파라미터 — 다양한 표현을 자동 변환 ──────────────────────
@router.get("/users/{user_id}")
async def get_user(user_id: int, active: bool = True):
    # bool 타입은 여러 표현을 자동으로 True / False 로 변환합니다
    #
    # True  로 변환되는 값: ?active=true  ?active=1  ?active=yes  ?active=on
    # False 로 변환되는 값: ?active=false ?active=0  ?active=no   ?active=off
    #
    # GET /users/123              → user_id=123, active=True   (기본값)  ✅
    # GET /users/123?active=false → user_id=123, active=False            ✅
    # GET /users/123?active=0     → user_id=123, active=False (0 → False) ✅
    # GET /users/123?active=xyz   → 422 (bool 변환 불가)                  ❌
    return {"user_id": user_id, "active": active}
    # 예상 응답 (/users/123): {"user_id": 123, "active": true}

# ── Optional 쿼리 파라미터 — 없어도 되는 값 ────────────────────────────────
from typing import Optional   # 또는 파이썬 3.10+에서는 str | None

@router.get("/items")
async def list_items(
    category: Optional[str] = None,   # None이 기본값 → 없어도 됨
    min_price: Optional[int] = None,  # 없으면 None → 코드에서 분기 처리
):
    # GET /items                          → category=None, min_price=None
    # GET /items?category=food            → category="food", min_price=None
    # GET /items?category=food&min_price=5 → category="food", min_price=5
    result = {}
    if category:
        result["category"] = category     # None이 아닐 때만 필터 적용
    if min_price is not None:
        result["min_price"] = min_price
    return result


'''

'''
   규칙 1. 경로 파라미터 : 데코레이터 URL에 {변수명} 이 있으면 → 경로 파라미터
    규칙 2. 바디 파라미터 : 함수 인자 타입이 Pydantic BaseModel 이면 → 요청 본문에서 읽음 (Day 8)
    규칙 3. 쿼리 파라미터 : 위 두 가지가 아닌 나머지 전부 → 쿼리 파라미터 (?key=value)  

    class UserCreate(BaseModel):
    name: str
    email: str

    class UserOut(BaseModel):
        id: int
        name: str

    @app.post("/users/{team_id}", response_model=UserOut)
    async def create_user(
        team_id: int,        # 규칙 1 → URL의 {team_id}와 이름이 같음 → 경로
        user: UserCreate,    # 규칙 2 → BaseModel이니까 → 요청 본문(JSON)
        notify: bool = True, # 규칙 3 → 나머지 → 쿼리 (?notify=false)
    ):
        return UserOut(id=1, name=user.name)   # ← 이건 규칙과 무관
    
                            인자의 BaseModel	                   response_model=
    방향	                들어옴 (요청 본문)	                    나감 (응답 본문)
    Fastapi가 하는 일 	    JSON → 파이썬 객체 변환 + 검증	         파이썬 객체 → JSON 변환 + 필드 필터링
    위치	                함수 괄호 안	                       데코레이터 안


'''