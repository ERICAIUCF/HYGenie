import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")

# API 키가 설정되지 않은 경우 오류 메시지 출력
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# 클라이언트에 API 키 전달
client = OpenAI(api_key=api_key)

# 어시스턴트 ID
#ASSISTANT_ID = "asst_YfPptwUj4Jky7AVIfd0hPR7X"
ASSISTANT_ID = "asst_o8bfAyGKf7mx6zYdrMXsIEFT"

# 세션 상태 초기화
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 스트림릿 앱 제목
st.markdown("""
    <style>
        .title-container {
            display: flex;
            align-items: center;
        }
        .title img {
            width: 5px;  /* 이미지 크기 조정 */
            height: 5px;  /* 이미지 크기 조정 */
            margin-right: 10px;  /* 이미지와 제목 사이의 간격 */
        }
        .title {
            font-size: 36px;
            font-weight: bold;
        }
    </style>
    <div class="title-container">
        <!-- 이미지가 제목 앞에 오도록 배치 -->
        <img src="https://phinf.pstatic.net/contact/20241217_116/1734410965291MnePL_PNG/image.png?type=s160" alt="이미지" />
        <div class="title" style="font-size: 55px; line-height: 1.1;">HY GENIE</div>

""", unsafe_allow_html=True)

# 앱 내용
st.markdown("""
    <style>
        .first-line {
            line-height: 1.2;  /* 첫 번째 줄의 행간 좁히기 */
            font-size: 15px;    /* 글씨 크기 줄이기 */
        }
        .second-line {
            line-height: 1.8;  /* 두 번째 줄의 행간 넓히기 */
            padding-bottom: 10px;  /* 경계선과 텍스트 간의 간격 조정 */
            font-size: 15px;    /* 글씨 크기 줄이기 */
        }
        .line-separator {
            border-top: 1.5px solid gray;  /* 회색 줄 추가 */
            margin-top: 10px;  /* 줄 위쪽 간격 넓히기 */
            margin-bottom: 20px;  /* 줄 아래쪽 간격 넓히기 */
        }
        .input-area {
            margin-top: 30px;  /* 질문 텍스트와 입력 필드 사이의 간격 넓히기 */
        }
    </style>
    <div class="first-line">
        <strong><span style="color: #0E4A84;">한양대학교 ERICA산학협력단</span></strong>  AI 매뉴얼 챗봇입니다.<br>
    </div>
    <div class="second-line">
        부정확한 답변이 포함될 수 있으니 답변의 출처를 통해 다시 한 번 확인해주세요.
    </div>
    <div class="line-separator"></div>  <!-- 회색 줄 추가 -->
""", unsafe_allow_html=True)



# 대화 내용 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 새로운 메시지 처리 함수
def process_input():
    if st.session_state.user_input:
        user_input = st.session_state.user_input
        
        # 새 스레드 생성 (처음 질문할 때만)
        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        # 사용자 메시지 추가
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # 실행 생성
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )

        # 실행 완료 대기
        with st.spinner('답변을 생성 중입니다...'):
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break

        # 메시지 가져오기
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # 메시지 업데이트
        st.session_state.messages = []
        for msg in reversed(messages.data):
            role = "사용자" if msg.role == "user" else "AI"
            content = msg.content[0].text.value
            st.session_state.messages.append({"role": role, "content": content})

        # 입력 필드 초기화
        st.session_state.user_input = ""

# 사용자 입력 (화면 하단에 위치)
st.text_input("질문을 입력하세요:", key="user_input", on_change=process_input)
