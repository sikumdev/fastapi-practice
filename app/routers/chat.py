# app/routers/chat.py
# 역할: /chat/ URL 수신, service 함수 호출, 응답 반환
# 이 파일은 LLM 호출 방법을 몰라도 됨 — get_chat_response() 를 호출만 함

from fastapi import APIRouter
from app.services.llm_service import get_chat_response
# services 레이어를 임포트 — routers는 services를 호출하지만
# services는 routers를 몰라야 합니다 (단방향 의존성)

router = APIRouter()

@router.post("/")
# prefix="/chat" (main.py에서 등록) + "/" → 실제 URL: POST /chat/
async def chat_endpoint(message: str, session_id: str = "default"):
    """
    AI 채팅 응답 엔드포인트

    현재 기초 버전: message는 쿼리 파라미터로 전달
    → POST /chat/?message=안녕&session_id=s1

    Day 8 업그레이드 예정: Pydantic ChatRequest 바디로 변경
    → POST /chat/ + JSON body {"message": "안녕", "session_id": "s1"}
    """
    # service 레이어에 실제 처리 위임 — 라우터는 호출만 함
    response = await get_chat_response(message, session_id)

    return {"message": response, "session_id": session_id}
    # 예상 응답: {"message": "안녕하세요!...", "session_id": "default"}

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
    방향	    들어옴 (요청 본문)	                    나감 (응답 본문)
    하는 일 	JSON → 파이썬 객체 변환 + 검증	        파이썬 객체 → JSON 변환 + 필드 필터링
    위치	        함수 괄호 안	                    데코레이터 안

    '''