# ────────────────────────────────────────────────────────────
# app/routers/chat.py — Pydantic 검증 + Depends 주입 + ainvoke 호출
# ────────────────────────────────────────────────────────────

# ① FastAPI 라우터와 의존성 주입 도구
import asyncio

from fastapi import APIRouter, Depends

# ② LangChain 체인 구성 요소
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ③ 이 모듈에서 정의한 의존성과 스키마 임포트
from app.dependencies import get_llm
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.sse import sse_event

router = APIRouter()


@router.post("/", response_model=ChatResponse)   # response_model: 응답 스키마 강제 + 자동 문서화
async def chat_endpoint(
    request: ChatRequest,                          # ← Pydantic이 자동 검증 (8-1에서 배운 것)
    llm: ChatOpenAI = Depends(get_llm),            # ← Depends가 자동 주입 (오늘 배우는 것)
):
    """AI 채팅 엔드포인트 — 검증된 요청을 받아 LLM으로 처리 후 반환."""

    # ④ LCEL 체인 조립 — Prompt → LLM → Parser
    prompt = ChatPromptTemplate.from_messages([
        ("system", "유용한 AI 어시스턴트입니다."),  
        ("human", "{message}"),
    ])
    chain = prompt | llm | StrOutputParser()
    # Day 7까지는 prompt | llm 이었고 result.content로 접근했으나,
    # 오늘부터 StrOutputParser()를 추가해 result가 바로 str로 반환됩니다.

    # ⑤ 비동기 호출 — async def 안에서는 반드시 ainvoke!
    result = await chain.ainvoke({"message": request.message})
    # result 타입: str (StrOutputParser 통과 후)
    # 예상 값: "안녕하세요! 무엇을 도와드릴까요?"

    # ⑥ 응답 객체 생성 — ChatResponse 스키마에 맞춰 반환
    return ChatResponse(
        message=result,
        session_id=request.session_id,   # 클라이언트가 보낸 session_id를 그대로 돌려줌
        model="gpt-4o-mini",
    )
    # 예상 JSON: {"message": "...", "session_id": "default", "model": "gpt-4o-mini", "tokens_used": null}

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "유용한 AI 어시스턴트입니다."),
    ("human", "{message}"),
])


@router.post("/stream-v2")
async def chat_stream_v2(
    request: ChatRequest,
    llm: ChatOpenAI = Depends(get_llm),
):
    """v2: SSE 형식 + [DONE] 신호 — 클라이언트가 종료를 감지할 수 있음"""
    chain = prompt_template | llm | StrOutputParser()

    async def generate():
        async for token in chain.astream({"message": request.message}):
            yield sse_event(token)                    # v1과 차이: SSE 형식으로 래핑
        yield sse_event("[DONE]", event="done")       # 종료 신호 추가

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},        # 중간 프록시의 캐싱 방지
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    llm: ChatOpenAI = Depends(get_llm),
):
    """v3: v2 + 에러 처리 + 프록시 버퍼링 방지 (프로덕션 수준)"""
    chain = prompt_template | llm | StrOutputParser()

    async def token_generator():
        """토큰을 하나씩 SSE 형식으로 yield하는 async generator"""
        try:
            async for token in chain.astream({"message": request.message}):
                yield sse_event(token)
                await asyncio.sleep(0)
                # asyncio.sleep(0): "이벤트 루프에 잠깐 제어권을 돌려줘"
                # 0초 대기가 아니라 다른 코루틴이 실행될 기회를 줍니다

            yield sse_event("[DONE]", event="done")   # 정상 완료 신호

        except Exception as e:
            # v2와 차이: 에러를 event: error 로 클라이언트에 전달
            yield sse_event(str(e), event="error")

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # nginx에게 "버퍼에 모으지 말고 즉시 전달해" 지시
            # 이 헤더 없이 nginx 뒤에 배포하면 9-3 트러블슈팅 표 1번 증상 발생
        },
    )



