from fastapi import FastAPI                    # FastAPI 클래스 임포트

app = FastAPI(
    title='Day 7 실습 — v1 최소 서버',
    description='모듈 7-1: 9줄짜리 첫 번째 FastAPI 서버',
    version='0.1.0',
)
# title= : /docs 상단에 표시되는 서비스 이름
# 이 변수명 "app"이 uvicorn 실행 명령에서 :app 에 해당 ("uvicorn minimal_app:app")

@app.get("/")
# @app.get("/") : 라우터 데코레이터 — "GET 메서드로 / 경로에 요청이 오면 아래 함수를 실행"
# HTTP 메서드(get)와 URL 경로("/")를 함수에 연결하는 역할
# FastAPI는 @app.post, @app.put, @app.delete 도 제공

async def root():
# async def : 비동기 함수 (Day 6 복습) — I/O 대기 중 다른 요청 처리 가능
# 함수명(root)은 /docs에 엔드포인트 이름으로 표시됨

    return {"message": "Hello, FastAPI!"}
    # dict를 return → FastAPI가 JSON으로 자동 변환
    # {"message": "Hello, FastAPI!"} → Content-Type: application/json
    # 예상 응답: {"message": "Hello, FastAPI!"}

@app.get("/health")
# /health : 서버 상태 확인 엔드포인트 — 거의 모든 서비스에 관례적으로 존재
# 로드 밸런서·모니터링 도구가 이 URL을 주기적으로 호출해 서버 생존을 확인

async def health():
    return {"status": "ok"}
    # 예상 응답: {"status": "ok"}
    # Day 7 실습 노트북()에서 이 응답을 httpx로 직접 확인합니다