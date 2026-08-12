# ────────────────────────────────────────────────────────────
# app/schemas/chat.py — v2: Field로 세밀한 제약 추가 (실제 서비스 수준)
# ────────────────────────────────────────────────────────────

# ① BaseModel에 Field를 추가로 임포트 — 제약 조건과 메타데이터를 함께 정의하는 함수
from pydantic import BaseModel, Field
# ※ Pydantic v2부터는 Optional[str] 대신 str | None 사용을 권장합니다
#   더 파이썬답고, Pydantic v2 내부 처리에도 최적화된 방식입니다

class ChatRequest(BaseModel):
    """클라이언트가 POST /chat/ 로 보내는 요청 형식.
       설계 변경 시 이 클래스도 함께 수정해야 루브릭 '설계서 정합성' 20점을 지킬 수 있습니다.
    """

    # ② message 필드 — 가장 중요한 필수 입력값
    message: str = Field(
        min_length=1,                          # 빈 문자열("") 차단 — 빈 프롬프트 방지
        max_length=2000,                       # 과도한 입력 차단 — 토큰 비용 폭탄 방지
        description="사용자 입력 메시지",        # /docs Swagger UI에 표시되는 필드 설명
        examples=["오늘 회의 내용을 요약해줘"],   # /docs Try it out 기능의 예시 값
    )

    # ③ session_id 필드 — 대화 이력 추적용 (선택 입력)
    session_id: str = Field(
        default="default",                     # 클라이언트가 보내지 않으면 "default" 사용
        description="대화 세션 구분자 (LangSmith 트레이스 필터에 활용 가능)",
    )

    # ④ temperature 필드 — LLM 창의성 조절 (선택 입력)
    temperature: float = Field(
        default=0.7,                           # 기본값: 적당히 창의적인 중간값
        ge=0.0,   # ge = greater than or equal → 0.0 미만 값 차단 (음수 방지)
        le=2.0,   # le = less than or equal   → 2.0 초과 값 차단 (OpenAI 허용 범위 상한)
        description="LLM 창의성 조절 (0=매번 같은 답변, 2=매번 다른 창의적 답변)",
    )


class ChatResponse(BaseModel):
    """서버가 반환하는 응답 형식.

    response_model=ChatResponse 로 엔드포인트에 등록하면:
    - 내부 전용 필드(예: 원가 정보)가 자동으로 제거됩니다 (보안)
    - /docs에 응답 스키마가 자동 문서화됩니다
    """

    message: str          = Field(description="AI 응답 내용")
    session_id: str       = Field(description="요청과 동일한 세션 ID (대화 추적용)")
    model: str            = Field(description="사용된 LLM 모델명 (예: gpt-4o-mini)")
    tokens_used: int | None = Field(
        default=None,
        description="사용된 토큰 수 — 현재는 None 반환, 향후 비용 추적에 활용 예정"
    )