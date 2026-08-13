# ────────────────────────────────────────────────────────────
# app/dependencies.py — LLM 클라이언트 의존성 정의
# ────────────────────────────────────────────────────────────

# ① 환경 변수 로드 — 반드시 ChatOpenAI 임포트보다 먼저!
from dotenv import load_dotenv
load_dotenv()   # .env에서 OPENAI_API_KEY 등 환경변수 로드
                # 이 줄이 없으면 ChatOpenAI() 초기화 시 401 Unauthorized 에러 발생

# ② 싱글턴 패턴을 위한 표준 라이브러리 데코레이터
from functools import lru_cache   # 함수 결과를 캐시 → 같은 인수면 재계산 없이 반환

# ③ LangChain OpenAI 연동 클라이언트
from langchain_openai import ChatOpenAI   # OPENAI_API_KEY 환경변수에서 자동 로드


@lru_cache()       # ← 이 데코레이터가 싱글턴을 만듭니다
def get_llm() -> ChatOpenAI:
    """LLM 클라이언트 팩토리 — 최초 1회 생성, 이후 캐시 반환.

    @lru_cache() 없이: 요청마다 ChatOpenAI() 생성 → 연결 낭비
    @lru_cache() 있으면: 최초 1회만 생성, 모든 요청이 같은 인스턴스 공유
    """
    return ChatOpenAI(
        model="gpt-4o-mini",   # 과정 표준 모델 — 빠른 응답, 저비용
        temperature=0,          # 일관된 출력 (기본값 0.7보다 낮춰 재현성 확보)
        # ✅ api_key는 환경변수(OPENAI_API_KEY)에서 자동 로드
        # ❌ 절대 금지: ChatOpenAI(api_key="sk-...")  ← 코드에 키 노출
    )

'''
MODEL_NAME = "gpt-4o-mini"

@lru_cache
def get_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", "유용한 AI 어시스턴트입니다."),
        ("human", "{message}"),
    ])

@lru_cache
def get_chain() -> Runnable[dict, str]:
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return get_prompt() | llm | StrOutputParser()

ChainDep = Annotated[Runnable[dict, str], Depends(get_chain)]
PromptDep = Annotated[ChatPromptTemplate, Depends(get_prompt)]


@lru_cache
def get_encoder(model: str = MODEL_NAME):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("o200k_base")  # gpt-4o 계열 기본 인코딩

'''

'''
Depends 없이 vs Depends 있이 — 두 패턴 비교

관점	        Depends 없이 (나쁜 예)      	    Depends 있이 (좋은 예)
LLM 초기화	    요청마다 ChatOpenAI() 호출  	   최초 1회만, 이후 캐시 반환
인스턴스 수	    동시 요청 100개 → 100개 생성	    동시 요청 100개 → 1개 공유
설정 관리	    각 함수마다 설정 반복	            get_llm() 한 곳에서 집중 관리
테스트	        LLM 호출 없이 테스트 불가	        dependency_overrides로 mock 교체
코드 중복	    엔드포인트마다 초기화 코드 복붙	    한 번 선언, 어디서든 재사용


# lru_cache 동작 원리 (의사 코드)
호출 1: get_llm()  →  ChatOpenAI() 생성 → 캐시 저장 → 반환
호출 2: get_llm()  →  캐시 확인 → 캐시 HIT → 저장된 인스턴스 반환 (생성 없음)
호출 3: get_llm()  →  캐시 확인 → 캐시 HIT → 저장된 인스턴스 반환 (생성 없음)
# 결과: 얼마나 많은 요청이 와도 ChatOpenAI()는 딱 한 번만 만들어짐

API 키가 교체되면 get_llm.cache_clear()로 비워야 새키가 반영됨?


'''