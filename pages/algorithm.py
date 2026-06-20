import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="추천 알고리즘 버블 체험", layout="wide")

# -------------------------
# 콘텐츠 데이터
# -------------------------
content_pool = [
    {"title": "⚽ 손흥민 멀티골!", "category": "스포츠"},
    {"title": "🏀 NBA 플레이오프 대이변", "category": "스포츠"},

    {"title": "🗳️ 대선 후보 토론 화제", "category": "정치"},
    {"title": "📢 정책 논쟁 격화", "category": "정치"},

    {"title": "🎮 신작 게임 출시", "category": "게임"},
    {"title": "🔥 프로게이머 역대급 플레이", "category": "게임"},

    {"title": "🎤 아이돌 컴백", "category": "연예"},
    {"title": "🎬 넷플릭스 신작 화제", "category": "연예"},

    {"title": "😱 충격! 믿기 힘든 사건", "category": "자극"},
    {"title": "🚨 지금 안 보면 손해", "category": "자극"},

    {"title": "📚 AI가 바꾸는 미래", "category": "교육"},
    {"title": "🧠 뇌는 어떻게 학습할까?", "category": "교육"},
]

categories = ["스포츠", "정치", "게임", "연예", "자극", "교육"]

# -------------------------
# 세션 상태
# -------------------------
if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in categories}

if "click_history" not in st.session_state:
    st.session_state.click_history = []

# -------------------------
# 추천 알고리즘
# -------------------------
def get_feed():
    weighted_pool = []

    for item in content_pool:
        weight = st.session_state.weights[item["category"]]
        weighted_pool.extend([item] * weight)

    return random.sample(weighted_pool, min(6, len(weighted_pool)))

def click_content(item):
    cat = item["category"]
    st.session_state.click_history.append(cat)
    st.session_state.weights[cat] += 3

# -------------------------
# 디지털 성향 분석
# -------------------------
def analyze_personality():
    history = st.session_state.click_history

    if len(history) == 0:
        return "분석 불가", "아직 데이터가 부족합니다."

    counts = {cat: history.count(cat) for cat in categories}
    dominant = max(counts, key=counts.get)
    unique_count = len(set(history))

    if unique_count >= 4:
        return "균형 탐색형 🌍", "다양한 관점의 콘텐츠를 고르게 소비하는 편입니다."

    if dominant == "스포츠":
        return "스포츠 몰입형 ⚽", "경쟁과 역동적인 콘텐츠를 선호합니다."

    elif dominant == "정치":
        return "이슈 집중형 🗳️", "사회적 이슈와 의견 중심 콘텐츠에 관심이 많습니다."

    elif dominant == "게임":
        return "몰입형 게이머 🎮", "재미와 몰입감을 주는 콘텐츠를 선호합니다."

    elif dominant == "연예":
        return "트렌드 민감형 🎤", "최신 유행과 화제에 민감합니다."

    elif dominant == "자극":
        return "자극 추구형 🚨", "강한 자극과 빠른 보상을 주는 콘텐츠에 끌립니다."

    elif dominant == "교육":
        return "지식 탐구형 📚", "학습과 정보 습득 중심 콘텐츠를 선호합니다."

    return "분석 중", ""

# -------------------------
# UI
# -------------------------
st.title("📱 추천 알고리즘 버블 체험")

st.markdown("""
### 프로그램 소개
당신은 SNS 사용자입니다.  
관심 있는 콘텐츠를 클릭해보세요.  
AI가 당신의 취향을 학습하며 추천 피드를 바꿉니다.

이 과정에서 추천 알고리즘이 어떻게 필터 버블을 만드는지 직접 체험해보세요.
""")

st.divider()

feed = get_feed()

st.subheader("📰 추천 피드")

cols = st.columns(2)

for i, item in enumerate(feed):
    with cols[i % 2]:
        st.markdown(f"### {item['title']}")
        st.caption(f"카테고리: {item['category']}")
        if st.button("보기", key=f"content_{i}"):
            click_content(item)
            st.rerun()

st.divider()

total_clicks = len(st.session_state.click_history)

# -------------------------
# 버블 심화 단계
# -------------------------
st.subheader("🫧 버블 심화 단계")

if total_clicks <= 2:
    st.success("1단계: 균형 상태 🌍")
    st.write("아직 다양한 콘텐츠가 추천되고 있습니다.")

elif total_clicks <= 5:
    st.warning("2단계: 버블 형성 시작 🫧")
    st.write("AI가 당신의 관심사를 학습하기 시작했습니다.")

elif total_clicks <= 9:
    st.error("3단계: 버블 심화 ⚠️")
    st.write("비슷한 콘텐츠가 피드의 대부분을 차지하고 있습니다.")

else:
    st.error("4단계: 필터 버블 고착화 🚨")
    st.write("AI가 거의 한 종류의 콘텐츠만 추천하고 있습니다.")

# -------------------------
# 알고리즘 분석
# -------------------------
st.divider()
st.subheader("📊 추천 알고리즘 분석")

df = pd.DataFrame({
    "카테고리": list(st.session_state.weights.keys()),
    "추천 강도": list(st.session_state.weights.values())
})

st.bar_chart(df.set_index("카테고리"))

# -------------------------
# 성향 분석 리포트
# -------------------------
st.divider()
st.subheader("📋 당신의 디지털 성향 분석 리포트")

ptype, desc = analyze_personality()

st.markdown(f"## {ptype}")
st.write(desc)

if total_clicks >= 5:
    dominant = max(st.session_state.weights, key=st.session_state.weights.get)

    st.markdown("### AI 추천 편향 분석")
    st.write(f"""
현재 알고리즘은 **{dominant}** 콘텐츠 중심으로 추천하고 있습니다.

즉, 당신의 정보 환경은 점점 특정 주제에 편향되고 있습니다.
""")

    st.info("""
### 버블 탈출 방법
- 평소 보지 않던 콘텐츠 클릭하기
- 반대 관점 콘텐츠 소비하기
- 추천 피드를 무비판적으로 믿지 않기
""")

# -------------------------
# 교육 포인트
# -------------------------
st.divider()
st.subheader("🎓 교육 포인트")

st.markdown("""
### 1. 필터 버블 (Filter Bubble)
AI는 사용자가 좋아할 콘텐츠만 보여줍니다.

### 2. 확증 편향 (Confirmation Bias)
기존 생각을 강화하는 정보만 소비하게 됩니다.

### 3. 추천 알고리즘 윤리
플랫폼은 체류 시간을 늘리는 방향으로 추천합니다.

### 생각해보기
TikTok, YouTube, Instagram 추천 알고리즘은  
당신에게 어떤 영향을 주고 있을까요?
""")

if st.button("🔄 초기화"):
    st.session_state.weights = {cat: 1 for cat in categories}
    st.session_state.click_history = []
    st.rerun()
