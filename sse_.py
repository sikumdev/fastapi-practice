'''
#### **세 가지 방식 비교 — SSE를 선택하는 이유**

LLM 서비스에서 실시간 데이터를 전달하는 방법은 크게 세 가지입니다.
방식	방향성	연결 방식	LLM 적합성	구현 복잡도	기존 인프라 호환
SSE	서버 → 클라이언트	HTTP 지속 연결	✅ 최적	낮음	✅ 그대로 사용
WebSocket	양방향	프로토콜 업그레이드	가능 (과잉 설계)	높음	⚠️ 추가 설정 필요
폴링	주기적 재요청	반복 HTTP 요청	❌ 비효율	낮음	✅ 그대로 사용

첫 번째 토큰이 도달하는 데 걸리는 시간을 TTFT(Time To First Token) 라고 합니다. 

	일반 HTTP (배치)	스트리밍 (SSE)
첫 응답까지 대기	5.0초	0.3~0.8초 (첫 토큰 기준)
사용자가 느끼는 속도	느림	3~5배 빠르게 체감
5초 동안 화면 상태	빈 화면 → 텍스트 전체	글자가 계속 타이핑됨
서버 자원 사용	생성 후 전송	생성과 전송 동시 진행
구현 복잡도	낮음	중간 (오늘 배울 내용)



# SSE 전체 스트림 예시 — "파이썬" 3글자를 3번에 나눠 전송하는 경우
# ─────────────────────────────────────────────────────────────
# 규칙:
#  · "event: [타입]" — 이벤트 종류 (생략 시 기본값 "message")
#  · "data: [내용]"  — 전달할 데이터 (JSON 형식 권장)
#  · 빈 줄 하나      — 이벤트 하나의 끝을 나타내는 구분자
# ─────────────────────────────────────────────────────────────


#### **SSE 프로토콜 구조 — 단순함이 강점**

SSE는 놀라울 정도로 단순한 텍스트 기반 프로토콜입니다. HTTP 응답 헤더에 `Content-Type: text/event-stream`을 설정하고 아래 형식으로 데이터를 계속 전송하면 됩니다.

event: message
data: {"content": "파"}

event: message
data: {"content": "이"}

event: message
data: {"content": "썬"}

event: done
data: {"content": "[DONE]"}

SSE 이벤트 타입 3가지
이벤트 타입	용도	data 필드 예시
message	토큰 하나 전달	{"content": "파이"}
done	스트리밍 완료 알림	{"content": "[DONE]"}
error	오류 발생 알림	{"content": "APIError: ..."}

 SSE 프로토콜은 event: [타입]\ndata: [JSON]\n\n 세 줄 반복

 
**async generator는 LLM 토큰 스트리밍을 위한 가장 자연스러운 파이썬 구조입니다.**

LangChain의 `chain.astream()`은 LLM이 토큰을 하나 생성할 때마다 즉시 반환합니다. 이 토큰들을 받아서 HTTP 채널로 흘려보내는 중간 역할이 필요한데, 이 역할에 정확히 맞는 파이썬 구조가 **async generator**입니다. “비동기로 여러 값을 하나씩 내보내는 함수”라는 개념이 처음에는 낯설게 느껴질 수 있지만, 원리를 이해하면 “이것 말고 다른 방법이 있을까?”라는 생각이 들 정도로 딱 맞는 추상화입니다.

이 모듈에서는 async generator의 개념을 이해한 뒤, SSE 유틸리티 함수를 작성하고 v1→v2→v3 단계로 스트리밍 엔드포인트를 완성합니다.

#### **네 가지 함수 유형 비교 — async generator의 위치**

파이썬에는 “동기/비동기” × “단일 반환/다중 반환” 조합으로 네 가지 함수 유형이 있습니다.

| 유형 | 선언 방식 | 반환 방식 | 소비 방법 | LLM 스트리밍 적합성 |
| --- | --- | --- | --- | --- |
| **일반 함수** | `def f():` | `return` 1회 | `result = f()` | ❌ 단일 반환 |
| **Generator 함수** | `def f(): yield` | `yield` 여러 번 | `for x in f():` | ❌ 동기만 |
| **async 함수** | `async def f():` | `return` 1회 | `result = await f()` | ❌ 단일 반환 |
| **async generator** | `async def f(): yield` | `yield` 여러 번 | `async for x in f():` | ✅ **최적** |

LLM 토큰 스트리밍에는 두 가지 조건이 동시에 필요합니다. ① LLM API 호출을 기다려야 하므로 **비동기** 필수, ② 토큰이 여러 개이므로 **다중 반환** 필수. 이 두 조건을 동시에 충족하는 것은 async generator 뿐

#### **LangChain `astream()`과 `token_generator`의 관계**

`chain.astream()`은 LangChain이 제공하는 async generator입니다. 우리가 작성하는 `token_generator()`는 그 위에서 **SSE 형식 변환을 담당하는 중간 레이어**입니다.

```
# 전체 데이터 흐름
# ─────────────────────────────────────────────────────────────────
#
#  1. 사용자 요청 (POST /chat/stream)
#       │  ChatRequest {"message": "질문"}
#       ▼
#  2. chain.astream({"message": "질문"})        ← LangChain async generator
#       │  LLM이 토큰 하나 생성 → 즉시 AIMessageChunk 반환
#       ▼
#  3. token_generator() [우리가 작성]           ← SSE 변환 담당
#       │  AIMessageChunk → sse_event(token) 호출
#       │  "event: message\ndata: {...}\n\n" 문자열 yield
#       ▼
#  4. StreamingResponse(token_generator(), ...)  ← FastAPI HTTP 레이어
#       │  HTTP chunked transfer encoding으로 청크 단위 전송
#       ▼
#  5. 클라이언트 (curl -N / httpx / Streamlit)
#
# ─────────────────────────────────────────────────────────────────

위 흐름에서 3번 단계만 우리가 작성합니다. LangChain(2번)은 토큰 생성을, FastAPI(4번)는 HTTP 전송을 각자 처리합니다. token_generator()의 유일한 책임은 “LangChain AIMessageChunk → SSE 형식 문자열”로 변환하는 것입니다. 단 이 역할 분리 때문에 chain.astream()의 에러가 token_generator() 안에서 잡혀야 합니다 — 바깥에서 잡으면 이미 StreamingResponse가 시작된 후라 HTTP 상태 코드를 바꿀 수 없습니다.
```


'''

# 네 유형 비교 — 동일한 "숫자 1, 2, 3을 비동기로 생성" 시나리오
import asyncio

# ① 일반 함수: 완성 후 리스트로 한 번에 → 스트리밍 불가
def f1():
    return [1, 2, 3]                         # 한 번에 전달

# ② Generator 함수: 하나씩이지만 동기 → await 불가
def f2():
    yield 1                                   # 일시 정지 → 1 전달
    yield 2                                   # 재개 → 2 전달
    yield 3                                   # 재개 → 3 전달

# ③ async 함수: 비동기지만 단일 반환 → 스트리밍 불가
async def f3():
    await asyncio.sleep(0)                    # 비동기 대기 가능
    return [1, 2, 3]                         # 하지만 한 번에 전달

# ④ async generator: 비동기 + 다중 반환 ← LLM 토큰 스트리밍에 정확히 대응
async def f4():
    for i in [1, 2, 3]:
        await asyncio.sleep(0)               # 각 토큰 생성 후 비동기 대기
        yield i                              # 하나씩 즉시 전달

# 소비 방법
result1 = f1()                               # [1, 2, 3]
for x in f2(): print(x)                     # 1, 2, 3 (동기)
result3 = asyncio.run(f3())                       # [1, 2, 3] ← Jupyter top-level await 전용

async def main():                                      #   .py에서는: asyncio.run(f3())
    async for x in f4(): print(x)               # 1, 2, 3 (비동기) ← 오늘 패턴
                                             #   Jupyter top-level await 전용
                                             #   .py에서는: async def main(): async for x in f4(): ...

asyncio.run(main())                                            
# 예상 출력: 1  2  3  (각 줄에 하나씩)