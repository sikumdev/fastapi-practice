# app/main.py
# 역할: 앱 초기화 + 라우터 등록 (안내 데스크)
# 이 파일은 "어떤 URL을 어느 라우터가 처리하는가"만 담당
# LLM 호출 코드, 프롬프트, 검증 로직은 절대 이 파일에 넣지 않습니다

# ────────────────────────────────────────────────────────────
# app/main.py — 전역 예외 핸들러 추가
# ────────────────────────────────────────────────────────────

# ① 예외 핸들러에 필요한 추가 임포트
from fastapi import FastAPI, Request         # Request: 핸들러에 요청 정보 전달
from fastapi.responses import JSONResponse   # 에러 응답을 JSON 형식으로 반환


from fastapi import FastAPI
from app.routers import chat, health, items
# from app.routers import chat  →  app/routers/chat.py 를 모듈로 임포트
# → 이 임포트가 성공하려면 app/__init__.py, app/routers/__init__.py 가 존재해야 함

app = FastAPI(
    title="LG CNS AI 서비스",                     # /docs 상단 서비스명
    description="MCP 기반 Agentic AI 서비스 개발자 과정 미니프로젝트",  # /docs 설명
    version="0.1.0",                              # /docs 버전 표시
)


# ② 전역 예외 핸들러 — Exception을 잡으면 모든 예상치 못한 에러를 처리
# ※ @app.exception_handler는 include_router() 전후 어디에 놓아도 동일하게 동작합니다
#   (미들웨어(@app.middleware)는 등록 순서가 중요하지만, 예외 핸들러는 무관합니다)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """LLM 타임아웃·API 키 만료·연결 오류 등 모든 예외를 500으로 통일.

    클라이언트에는 안전한 메시지만, 상세 오류는 서버 로그에만 기록합니다.
    """
    # ③ 실제 서비스에서는 여기에 로깅 추가 (Sentry, CloudWatch 등)
    # import logging
    # logging.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(status_code=500,content={"detail": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
        # ❌ 절대 금지: content={"detail": str(exc)}  ← 내부 구조·스택 트레이스 노출
        # ✅ 사용자에게는 안전한 메시지, 로그에만 상세 기록
    )


# include_router: "이 라우터를 앱에 연결해라" — 부서를 안내 데스크에 등록하는 것
app.include_router(health.router)
# health.router: health.py 안의 router = APIRouter() 인스턴스
# prefix 없음 → health.py 안의 @router.get("/health") 가 그대로 /health

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
# prefix="/chat" → chat.py 안의:
#   @router.post("/")       → 실제 등록 URL: POST /chat/
#   @router.post("/stream") → 실제 등록 URL: POST /chat/stream  
# tags=["Chat"] → /docs에서 Chat 그룹으로 묶임

app.include_router(items.router, tags=["Items Practice"])

