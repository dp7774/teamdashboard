from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# =========================================================
# 1. 데이터 불러오기
# =========================================================

TARGET_CSV = 'data1.csv'

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / TARGET_CSV

df = pd.read_csv(
    DATA_PATH,
    encoding='euc-kr'
)


# =========================================================
# 2. 입항 데이터 만들기
# =========================================================

beta_visit = df[
    df['수출입구분'] == '입항'
][
    ['월', '선종명', '전체선박수']
].copy()


# =========================================================
# 3. Streamlit 기본 설정
# =========================================================

st.set_page_config(
    page_title='2024 부산항 입항 선박 대시보드',
    layout='wide'
)



st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.title('2024 부산항 입항 선박 현황')

st.caption(
    '부산항 입항 선박의 선종별 비중과 월별 입항 패턴을 확인합니다.'
)


# =========================================================
# 4. 사이드바 필터
# =========================================================

with st.sidebar:
    st.header('조회 조건')

    # 월 범위 필터
    month_range = st.slider(
        '월 범위',
        min_value=1,
        max_value=12,
        value=(1, 12)
    )

    # 선종 목록
    ship_types = sorted(
        beta_visit['선종명']
        .dropna()
        .unique()
        .tolist()
    )

    # 선종 선택 필터
    selected_ship_types = st.multiselect(
        '선종 선택',
        options=ship_types,
        default=ship_types
    )


# 조원 링크

with st.sidebar:
    st.header('현재 대시보드')

    st.button(
        '신예지 | 2024 부산항 입항 선박 현황'
    )

with st.sidebar:
    st.header('팀원 대시보드 바로가기')
    st.link_button(
        '옥재승 | 항만 컨테이너 물동량',
        'https://dpzxrhykwvuj5uy8qyor5c.streamlit.app/'
    )

# =========================================================
# 5. 필터 적용
# =========================================================

filtered_visit = beta_visit[
    (beta_visit['월'] >= month_range[0])
    &
    (beta_visit['월'] <= month_range[1])
].copy()


filtered_visit = filtered_visit[
    filtered_visit['선종명'].isin(selected_ship_types)
].copy()


# =========================================================
# 6. 선종별 입항 비중
# =========================================================

ship_share = (
    filtered_visit
    .groupby(
        '선종명',
        as_index=False
    )['전체선박수']
    .sum()
)

total_ships = ship_share['전체선박수'].sum()


if total_ships > 0:
    ship_share['입항비중(%)'] = (
        ship_share['전체선박수']
        / total_ships
        * 100
    ).round(2)
else:
    ship_share['입항비중(%)'] = 0


ship_share = ship_share.sort_values(
    by='전체선박수',
    ascending=False
).reset_index(drop=True)


# =========================================================
# 7. 월별 입항 선박 수
# =========================================================

monthly_visit = (
    filtered_visit
    .groupby(
        '월',
        as_index=False
    )['전체선박수']
    .sum()
)

monthly_visit = monthly_visit.sort_values(
    by='월'
).reset_index(drop=True)


# =========================================================
# 8. 전월 대비 입항량 증감률
# =========================================================

monthly_visit['전월대비증감률(%)'] = (
    monthly_visit['전체선박수']
    .pct_change()
    * 100
).round()


# =========================================================
# 9. KPI 계산
# =========================================================

# 총 입항 선박 수
total_visit = filtered_visit['전체선박수'].sum()


# 최다 입항 선종
if not ship_share.empty:
    top_ship_type = ship_share.iloc[0]['선종명']
    top_ship_count = int(
        ship_share.iloc[0]['전체선박수']
    )
else:
    top_ship_type = '-'
    top_ship_count = 0


# 최다 입항 월
if not monthly_visit.empty:
    top_month_row = monthly_visit.loc[
        monthly_visit['전체선박수'].idxmax()
    ]

    top_month = int(
        top_month_row['월']
    )

    top_month_count = int(
        top_month_row['전체선박수']
    )
else:
    top_month = 0
    top_month_count = 0


# 월평균 입항 선박 수
if not monthly_visit.empty:
    avg_monthly_visit = (
        monthly_visit['전체선박수']
        .mean()
    )
else:
    avg_monthly_visit = 0


# =========================================================
# 10. KPI 카드 출력
# =========================================================

st.subheader('핵심 지표')

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        label='월평균 입항 선박 수',
        value=f'{avg_monthly_visit:,.0f}척',
        border=True
    )


with col2:
    st.metric(
        label='총 입항 선박 수',
        value=f'{total_visit:,}척',
        border=True
    )


with col3:
    st.metric(
        label='최다 입항 선종',
        value=top_ship_type,
        border=True
    )


with col4:
    st.metric(
        label='최다 입항 월',
        value=f'{top_month}월' if top_month != 0 else '-',
        border=True
    )


st.divider()


# =========================================================
# 11. 그래프 2열 배치
# =========================================================

col_left, col_right = st.columns(2)


# -----------------------------
# 왼쪽: 선종별 입항 비중
# -----------------------------

with col_left:
    st.subheader('선종별 입항 비중')

    fig_share = px.bar(
        ship_share,
        x='선종명',
        y='입항비중(%)',
        title='선종별 입항 비중'
    )

    st.plotly_chart(
        fig_share,
        use_container_width=True
    )


# -----------------------------
# 오른쪽: 월별 입항 선박 수
# -----------------------------

with col_right:
    st.subheader('월별 입항 선박 수')

    fig_monthly = px.line(
        monthly_visit,
        x='월',
        y='전체선박수',
        markers=True,
        title='월별 입항 선박 수'
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )


# =========================================================
# 12. 전월 대비 증감률 그래프
# =========================================================

st.subheader('전월 대비 입항량 증감률')

fig_growth = px.line(
    monthly_visit,
    x='월',
    y='전월대비증감률(%)',
    markers=True,
    title='전월 대비 입항량 증감률'
)
st.caption(
    '1월은 비교 월이 없어 제외 하였습니다.'
)


st.plotly_chart(
    fig_growth,
    use_container_width=True
)



# =========================================================
# 13. 상관계수 + 회귀선
# =========================================================

# 1에 가까움   → 강한 양의 상관
# 0에 가까움   → 관계가 약함
# -1에 가까움  → 강한 음의 상관
# 월별 입항 선박 수와 전월 대비 증감률은 수학적으로 어느 정도 연결된 값
# 증감률 자체가 이번 달 입항량을 이용해서 계산된 값

st.subheader('월별 입항 선박 수와 전월 대비 증감률의 관계')

# 1월은 전월 대비 증감률이 NaN이므로 제거
corr_df = monthly_visit.dropna(
    subset=['전월대비증감률(%)']
).copy()


st.caption(
    '월별 입항 선박 수와 전월 대비 증감률의 상관계수는 0.81로 나타났으나, '
    '증감률이 입항 선박 수를 기반으로 산출된 지표이므로 해석에 주의가 필요합니다.'
)


# 상관계수
corr_value = corr_df['전체선박수'].corr(
    corr_df['전월대비증감률(%)']
)


# 회귀선 계산
slope, intercept = np.polyfit(
    corr_df['전체선박수'],
    corr_df['전월대비증감률(%)'],
    1
)


# 산점도 생성
fig_scatter = go.Figure()


# 월별 관측치
fig_scatter.add_trace(
    go.Scatter(
        x=corr_df['전체선박수'],
        y=corr_df['전월대비증감률(%)'],
        mode='text+markers',
        text=corr_df['월'].astype(str) + '월',
        textposition='top center',
        name='월별 관측치'
    )
)


# 회귀선용 x 범위
x_range = [
    corr_df['전체선박수'].min(),
    corr_df['전체선박수'].max()
]


# 회귀선 추가
fig_scatter.add_trace(
    go.Scatter(
        x=x_range,
        y=[
            slope * x + intercept
            for x in x_range
        ],
        mode='lines',
        name='회귀선'
    )
)


fig_scatter.update_layout(
    title=f'입항 선박 수와 증감률의 관계 (상관계수: {corr_value:.2f})',
    xaxis_title='월별 입항 선박 수',
    yaxis_title='전월 대비 증감률(%)'
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)




# =========================================================
# 14. 필터링된 데이터 확인
# =========================================================

st.subheader('조회 데이터')

st.dataframe(
    filtered_visit,
    hide_index=True,
    use_container_width=True
)