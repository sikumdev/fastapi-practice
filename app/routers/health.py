# app/routers/health.py
# 역할: GET /health 엔드포인트 하나만 담당
# 서비스 로직이 없으므로 services/ 를 임포트하지 않음

from fastapi import APIRouter

router = APIRouter()
# APIRouter(): 이 파일만의 라우터 인스턴스
# main.py 의 FastAPI() 앱 전체와 다름 — 부서 내 담당자 수준
# main.py에서 app.include_router(health.router)로 앱에 연결됨

@router.get("/health", tags=["Health"])
# @router.get → APIRouter 인스턴스의 GET 등록 (app.get 이 아님!)
# "/health" → main.py에서 prefix 없이 등록되므로 실제 URL도 /health
# tags=["Health"] → /docs에서 Health 그룹으로 표시
async def health_check():
    """
    서버 상태를 확인합니다.
    로드 밸런서·쿠버네티스·모니터링 도구가 주기적으로 호출합니다.
    이 엔드포인트가 200을 반환하면 "서버 정상"으로 판단합니다.
    """
    return {"status": "ok", "service": "lgcns-ai-service"}
    # dict 반환 → FastAPI가 JSON 자동 변환
    # 예상 응답: {"status": "ok", "service": "lgcns-ai-service"}


#====
'''
await 쓸 게 있으면 async def, 없으면 그냥 def, 근데 I/O 자체가 없으면 async def


함수                                안 내용	             써야 할 것
I/O 없음                        (dict 리턴, 계산)	        async def
await 붙는 라이브러리               (httpx, asyncpg)	    async def
await 안 붙는 라이브러리           (requests, psycopg2)	     def
async def + 블로킹 코드	절대 금지 ☠️


'''