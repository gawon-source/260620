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
# UI
# -------------------------
st.title("📱 추천 알고리즘 버블 체험")
st.markdown("""
당신은 SNS 사용자입니다.  
관심 있는 콘텐츠를 클릭해보세요.  
AI가 당신의 취향을 학습합니다.
""")

st.divider()

feed = get_feed()

st.subheader("추천 피드")

cols = st.columns(2)

for i, item in enumerate(feed):
    with cols[i % 2]:
        st.markdown(f"### {item['title']}")
        st.caption(f"카테고리: {item['category']}")
        if st.button("보기", key=f"content_{i}"):
            click_content(item)
            st.rerun()

st.divider()

st.subheader("추천 알고리즘 분석")

df = pd.DataFrame({
    "카테고리": list(st.session_state.weights.keys()),
    "추천 강도": list(st.session_state.weights.values())
})

st.bar_chart(df.set_index("카테고리"))

if len(st.session_state.click_history) >= 3:
    dominant = max(st.session_state.weights, key=st.session_state.weights.get)

    st.subheader("AI 분석 결과")
    st.warning(f"""
현재 알고리즘은 **{dominant}** 콘텐츠를 가장 선호한다고 판단했습니다.

당신의 피드는 점점 이 콘텐츠 중심으로 바뀌고 있습니다.
""")

    st.error("""
### 필터 버블 발생
이제 AI는 당신이 좋아하는 콘텐츠만 보여주기 시작합니다.

문제점:
- 다양한 관점을 보기 어려움
- 기존 생각이 강화됨
- 편향이 커질 수 있음
""")

st.divider()

st.subheader("교육 포인트")

st.markdown("""
### 필터 버블 (Filter Bubble)
사용자가 좋아할 만한 정보만 제공

### 확증 편향 (Confirmation Bias)
자신의 기존 생각을 강화

### 추천 알고리즘 윤리
AI는 체류 시간을 늘리는 방향으로 최적화됨

### 생각해보기
TikTok / YouTube 추천 알고리즘은  
당신에게 어떤 영향을 주고 있을까요?
""")

if st.button("초기화"):
    st.session_state.weights = {cat: 1 for cat in categories}
    st.session_state.click_history = []
    st.rerun()
