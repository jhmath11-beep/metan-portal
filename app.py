import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="중등 청간전보 분석", layout="wide")
st.title("📍 중등 청간전보 커트라인 (최근 5개년)")

# 2. 통합 데이터 불러오기
@st.cache_data
def load_data():
    # 데이터 통합 단계에서 만든 파일을 읽어옵니다.
    df = pd.read_csv("total_data.csv")
    return df

try:
    df = load_data()
    
    # --- 사이드바: 조건 선택 ---
    st.sidebar.header("🔍 검색 조건 설정")
    
    # 과목 선택
    all_subjects = sorted(df['교과'].unique())
    selected_subject = st.sidebar.selectbox("과목을 선택하세요", all_subjects)
    
    # 순위별 지역 선택 (1~3순위)
    all_regions = sorted(df['지역'].unique())
    
    st.sidebar.subheader("지역 순위 설정")
    rank1 = st.sidebar.selectbox("1순위 지역", all_regions, index=0)
    rank2 = st.sidebar.selectbox("2순위 지역", all_regions, index=1)
    rank3 = st.sidebar.selectbox("3순위 지역", all_regions, index=2)
    
    selected_regions = [rank1, rank2, rank3]
    
    # --- 데이터 필터링 ---
    # 선택한 과목과 1, 2, 3순위 지역에 해당하는 데이터만 추출
    filtered_df = df[(df['교과'] == selected_subject) & (df['지역'].isin(selected_regions))]
    
    # --- 시각화 섹션 ---
    st.subheader(f"📈 {selected_subject} - 순위별 지역 커트라인 추이")
    
    if not filtered_df.empty:
        # 연도별 커트라인 그래프 (순위 지역별로 색상 구분)
        fig = px.line(filtered_df, x='연도', y='커트라인', color='지역',
                     markers=True, 
                     title=f"{selected_subject} 과목의 선택 지역 커트라인 변화",
                     labels={'커트라인': '커트라인 점수', '연도': '연도'})
        
        # 순위 정보를 강조하기 위해 범례 정렬 등을 조정할 수 있습니다.
        st.plotly_chart(fig, use_container_width=True)
        
       # --- 표 섹션 ---
        st.divider()
        st.subheader("📋 순위지역 - 연도별 정보 상세 표")
        
        # 1. 피벗 테이블 생성
        # aggfunc='first'를 추가하여 만에 하나 중복 데이터가 있어도 오류를 방지합니다.
        table_df = filtered_df.pivot_table(index='지역', columns='연도', values='커트라인', aggfunc='first')
        
        # 2. 1, 2, 3순위 순서대로 표 행 정렬
        # 존재하는 인덱스만 필터링하여 reindex 오류를 방지합니다.
        existing_regions = [r for r in selected_regions if r in table_df.index]
        table_df = table_df.reindex(existing_regions)

        # 3. 숫자 포맷팅 (5.000 -> 5, 4.400 -> 4.4)
        # applymap 대신 최신 문법인 map을 사용합니다.
        formatted_table = table_df.map(lambda x: f"{x:g}" if pd.notnull(x) else "-")
        
        # 4. 출력 (중요: 반드시 formatted_table을 넣어야 합니다!)
        st.table(formatted_table)
        
    else:
        st.warning("선택하신 조건에 해당하는 데이터가 없습니다. 지역이나 과목을 다시 확인해주세요.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("데이터 통합 파일(total_data.csv)이 정상적으로 생성되었는지 확인해주세요.")