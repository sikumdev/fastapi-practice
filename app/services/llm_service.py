# app/services/llm_service.py
# 역할: "실제로 LLM을 어떻게 호출하는가"만 담당
# routers/가 이 파일의 함수를 "호출"만 함 — 로직을 이해할 필요 없이

# ── ① 환경변수 로드 (필수! 없으면 401 AuthenticationError) ──────────────
from dotenv import load_dotenv
load_dotenv()   # .env 파일 → 환경변수로 등록
                # 이 줄이 없으면 OPENAI_API_KEY를 못 읽어 첫 호출부터 에러

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# ── ② LLM 비즈니스 로직 함수 ──────────────────────────────────────────────
async def get_chat_response(message: str, session_id: str) -> str:
    """
    사용자 메시지를 받아 LLM 응답 텍스트를 반환합니다.

    Args:
        message   : 사용자 입력 텍스트 (routers/chat.py에서 전달)
        session_id: 세션 식별자
                    현재는 미사용 — 8/18 DB 기반 대화 이력 구현 시 활용 예정
    Returns:
        str: LLM 응답 텍스트 (AIMessage.content)
    """
    # LLM 인스턴스 생성 — Day 8에서 Depends로 싱글턴 패턴으로 개선
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 프롬프트 템플릿 (Day 2 복습 — ChatPromptTemplate + 변수)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "유용한 AI 어시스턴트입니다. 한국어로 친절하게 답하세요."),
        ("human", "{message}"),   # {message} 자리에 사용자 입력이 채워짐
    ])

    chain = prompt | llm          # LCEL 파이프 (Day 3 복습)
                                  # PromptTemplate → ChatOpenAI 순서로 실행

    result = await chain.ainvoke({"message": message})
    # await   : 비동기 — LLM 응답 기다리는 동안 다른 요청 처리 가능 (Day 6 복습)
    # ainvoke : async 버전 invoke — async def 안에서는 반드시 ainvoke!
    # {"message": message} : 프롬프트 템플릿의 {message} 자리에 채울 값

    return result.content
    # result  : AIMessage 객체 (메시지 전체)
    # .content: 그 중 텍스트만 추출
    # 예상 반환: "안녕하세요! 무엇을 도와드릴까요?"