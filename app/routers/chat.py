# ────────────────────────────────────────────────────────────
# app/routers/chat.py — Pydantic 검증 + Depends 주입 + ainvoke 호출
# ────────────────────────────────────────────────────────────

# ① FastAPI 라우터와 의존성 주입 도구
from fastapi import APIRouter, Depends

# ② LangChain 체인 구성 요소
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import tiktoken

# ③ 이 모듈에서 정의한 의존성과 스키마 임포트
from app.dependencies import get_chain
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse,
                  summary="AI 채팅 응답",                  # /docs 엔드포인트 목록의 굵은 제목
                  description="사용자 메시지에 대한 AI 응답을 반환합니다. LangSmith에 자동 기록됩니다.",
                  responses={                              # 정상(200) 외의 응답 케이스 문서화
                      422: {"description": "입력 검증 실패 (메시지 길이, 온도 범위 등)"},
                      500: {"description": "LLM 호출 실패"},
                  },)   # response_model: 응답 스키마 강제 + 자동 문서화

async def chat_endpoint(
    request: ChatRequest,                          # ← Pydantic이 자동 검증 
    chain: Runnable[dict, str] = Depends(get_chain),            # ← Depends가 자동 주입
    # chain: ChainDep, prompt: PromptDep
):
    # ② 함수 docstring → /docs "Description" 섹션에 마크다운으로 렌더링
    """
    ## 사용 예시
    - "이 이메일의 핵심 요청을 요약해줘"
    - "이 민원을 유형별로 분류해줘"
    - "다음 텍스트를 영어로 번역해줘"

    ## 응답 구조
    - **message**: AI의 답변 텍스트
    - **session_id**: 요청과 동일한 세션 ID (대화 추적용)
    - **model**: 사용된 모델명 (gpt-4o-mini)
    """


    result = await chain.ainvoke({"message": request.message})
    # result 타입: str (StrOutputParser 통과 후)
    # 예상 값: "안녕하세요! 무엇을 도와드릴까요?"

    # 토큰 사용량 측정하기 
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    

    '''
    async def chat_endpoint(request: ChatRequest, chain: ChainDep, prompt: PromptDep):

    messages = prompt.format_messages(message=request.message)
    enc = get_encoder()
    tokens_used = sum(len(enc.encode(m.content)) for m in messages)
    

    response = await chain.ainvoke({"message": request.message})

    usage = response.usage_metadata
    # {'input_tokens': 24, 'output_tokens': 15, 'total_tokens': 39}

    return ChatResponse(
        message=response.content,
        session_id=request.session_id,
        model=MODEL_NAME,
        tokens_used=usage["total_tokens"],
    )
    
    '''


    # ⑥ 응답 객체 생성 — ChatResponse 스키마에 맞춰 반환
    return ChatResponse(
        message=result,
        session_id=request.session_id,   # 클라이언트가 보낸 session_id를 그대로 돌려줌
        model="gpt-4o-mini",
        tokens_used=len(enc.encode("유용한 AI 어시스턴트입니다."+request.message))
    )
    # 예상 JSON: {"message": "...", "session_id": "default", "model": "gpt-4o-mini", "tokens_used": null}


'''
FastAPI의 이벤트 루프는 단일 스레드입니다. 
invoke()처럼 LLM 응답을 기다리는 동기 작업이 루프를 점령하면, 
그 3~10초 동안 모든 다른 요청이 응답 불가 상태가 됩니다. 
접속자 10명 중 1명이 동기 호출을 쓰면 나머지 9명도 피해를 봅니다.
'''

'''
- **Depends = 선언형 의존성**: “나는 LLM이 필요해”라고 선언만 하면 FastAPI가 초기화·주입·에러 처리를 대신 담당
- **`@lru_cache()` = 싱글턴 패턴**: 최초 1회만 `ChatOpenAI()` 생성, 이후 모든 요청이 같은 인스턴스 공유 — 연결 낭비 없음
- **async def → ainvoke 필수**: 동기 `invoke()`는 이벤트 루프를 점령해 서버 전체를 멈춤 — Day 6 규칙의 실전 적용
- **테스트 용이성**: `app.dependency_overrides[get_llm] = get_mock_llm`으로 실제 LLM 없이 테스트 가능
#?? 마지막 테스트 용이성 이해가 안가
'''