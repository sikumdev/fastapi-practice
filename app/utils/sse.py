# app/utils/sse.py
import json   # SSE data 필드에 JSON 직렬화를 위해 필요

def sse_event(data: str, event: str = "message") -> str:
    """
    SSE(Server-Sent Events) 형식 문자열을 생성합니다.

    SSE 프로토콜 규칙 (9-1에서 학습한 내용):
      · "event: [타입]\n"  — 이벤트 종류 지정 (기본값 "message")
      · "data: [JSON]\n"   — 전달할 데이터 (JSON 형식 권장)
      · "\n"               — 이벤트 끝 구분자 (빈 줄 하나)
      ※\n = 실제 줄바꿈 문자. 함수 반환값에서는 f-string의\n이 실제 newline으로 치환됩니다.
    """
    return (
        f"event:{event}\n"
        f"data:{json.dumps({'content': data}, ensure_ascii=False)}\n\n"
        # ensure_ascii=False: 한국어 등 비ASCII 문자를 유니코드 이스케이프 없이 전달
    )

# repr() 어떤 함수인지??

# 동작 확인 (터미널에서 python app/utils/sse.py 로 실행)
if __name__ == "__main__":
    print(repr(sse_event("안녕")))
    # 예상 출력: 'event: message\ndata: {"content": "안녕"}\n\n'

    print(repr(sse_event("[DONE]", event="done")))
    # 예상 출력: 'event: done\ndata: {"content": "[DONE]"}\n\n'


'''
import httpx, json
import asyncio

BASE_URL = 'http://localhost:8000'   # 팀 서버 주소

async def stream_chat(message: str, session_id: str = 'step2-test'):
    # SSE 스트림을 한 줄씩 읽어 토큰을 출력합니다
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60) as client:
        async with client.stream(
            'POST', '/chat/stream',
            json={'message': message, 'session_id': session_id},
        ) as resp:
            print(f'상태 코드: {resp.status_code}')    # 예상: 200
            print('스트림 수신 중: ', end='', flush=True)
            async for line in resp.aiter_lines():       # SSE 한 줄씩 읽기
                if line.startswith('data:'):
                    # data: {"content": "파"}
                    data = json.loads(line[5:])         # 'data:' 이후 JSON 파싱
                    content = data.get('content', '')
                    if content == '[DONE]':             # 종료 신호
                        print('\n✅ 스트리밍 완료')
                        break
                    print(content, end='', flush=True)  # 토큰 즉시 출력
                    # flush=True → 파이썬은 출력을 모아뒀다 한꺼번에 내보내는 습관이 있는데, 이걸 끄고 즉시 화면에 찍습니다. 실시간 느낌

asyncio.run(stream_chat('파이썬이 뭐야?'))

'''