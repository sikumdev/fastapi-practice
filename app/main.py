# app/main.py
# 역할: 앱 초기화 + 라우터 등록 (안내 데스크)
# 이 파일은 "어떤 URL을 어느 라우터가 처리하는가"만 담당
# LLM 호출 코드, 프롬프트, 검증 로직은 절대 이 파일에 넣지 않습니다

from fastapi import FastAPI
from app.routers import chat, health, items
# from app.routers import chat  →  app/routers/chat.py 를 모듈로 임포트
# → 이 임포트가 성공하려면 app/__init__.py, app/routers/__init__.py 가 존재해야 함

app = FastAPI(
    title="LG CNS AI 서비스",                     # /docs 상단 서비스명
    description="MCP 기반 Agentic AI 서비스 개발자 과정 미니프로젝트",  # /docs 설명
    version="0.1.0",                              # /docs 버전 표시
)


# include_router: "이 라우터를 앱에 연결해라" — 부서를 안내 데스크에 등록하는 것
app.include_router(health.router)
# health.router: health.py 안의 router = APIRouter() 인스턴스
# prefix 없음 → health.py 안의 @router.get("/health") 가 그대로 /health

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
# prefix="/chat" → chat.py 안의:
#   @router.post("/")       → 실제 등록 URL: POST /chat/
#   @router.post("/stream") → 실제 등록 URL: POST /chat/stream  (Day 9에서 추가)
# tags=["Chat"] → /docs에서 Chat 그룹으로 묶임

app.include_router(items.router, tags=["Items"])