import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(page_title="스마트카드(852352) 수출 분석", layout="wide")

st.title("💳 스마트카드(HS 852352) 한국 수출 분석 대시보드")
st.markdown("본 대시보드는 2023년 BACI 데이터를 기반으로 2020-2023 가상 시나리오 분석을 제공합니다.")

# 1. 데이터 불러오기 및 852352 필터링
@st.cache_data
def load_smartcard_data():
    # 파일 경로 (본인의 환경에 맞게 수정 확인)
    try:
        baci_korea = pd.read_csv("./file/baci_korea_only.csv")
        country_codes = pd.read_csv("./file/country_codes_V202501.csv")
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return pd.DataFrame()
    
    # 852352 품목만 즉시 필터링
    df_85 = baci_korea[baci_korea["k"] == 852352].copy()
    
    # 국가 코드 매핑
    if 'country_code' in country_codes.columns:
        country_codes = country_codes.rename(columns={"country_code": "j"})
    
    df = pd.merge(df_85, country_codes, on="j", how="left")
    df = df[["t", "i", "country_name", "k", "v", "q"]]
    df = df.rename(columns={"country_name": "j"})
    
    # 랜덤 연도 생성 (2020~2023)
    np.random.seed(42)
    df["t"] = np.random.randint(2020, 2024, size=len(df))
    
    return df

df = load_smartcard_data()

if not df.empty:
    # 2. 요약 지표 (Metrics)
    total_val = df['v'].sum()
    total_qty = df['q'].sum()
    avg_unit_price = total_val / total_qty if total_qty > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("누적 수출액 (852352)", f"${total_val:,.0f} (k)")
    with col2:
        st.metric("누적 수출 중량", f"{total_qty:,.1f} Ton")
    with col3:
        st.metric("평균 단가 ($/kg)", f"{avg_unit_price:.2f}")

    st.divider()

    # 3. 메인 분석 - 히트맵과 연도별 추이
    row1_col1, row1_col2 = st.columns([2, 1])

    with row1_col1:
        st.subheader("🌐 주요 수출국별 연도별 흐름 (Heatmap)")
        # 상위 10개국 추출
        country_rank = df.groupby("j")["v"].sum().sort_values(ascending=False)
        top_10 = country_rank.head(10).index
        df_top10 = df[df["j"].isin(top_10)]
        
        if not df_top10.empty:
            # 피벗 테이블 생성 시 빈 값을 0으로 채우는 .fillna(0) 추가
            pivot_df = df_top10.pivot_table(index="j", columns="t", values="v", aggfunc="sum").fillna(0)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
            plt.ylabel("수입국")
            plt.xlabel("연도")
            st.pyplot(fig)
        else:
            st.write("표시할 데이터가 없습니다.")

    with row1_col2:
        st.subheader("📅 연도별 수출 비중")
        yearly_v = df.groupby("t")["v"].sum()
        if not yearly_v.empty:
            fig2, ax2 = plt.subplots()
            ax2.pie(yearly_v, labels=yearly_v.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
            st.pyplot(fig2)

    st.divider()

    # 4. 상세 데이터 테이블
    st.subheader("📊 국가별 상세 수출 통계 (금액 순)")
    country_detail = df.groupby("j").agg({
        'v': 'sum',
        'q': 'sum'
    }).reset_index()
    country_detail['unit_price'] = country_detail['v'] / country_detail['q']
    country_detail = country_detail.sort_values('v', ascending=False).reset_index(drop=True)
    country_detail.columns = ['국가명', '총 수출액($1,000)', '총 중량(Ton)', '평균 단가']

    st.dataframe(country_detail.style.format({
        '총 수출액($1,000)': '{:,.0f}',
        '총 중량(Ton)': '{:,.2f}',
        '평균 단가': '{:,.2f}'
    }), use_container_width=True)

    # 5. 사이드바 - 설정 및 다운로드
    st.sidebar.title("🛠 설정")
    st.sidebar.info("품목: 852352 (스마트카드)\n대상: 한국 수출 데이터")

    # 데이터 다운로드 버튼
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="전체 필터링 데이터 다운로드",
        data=csv,
        file_name='korea_smartcard_export.csv',
        mime='text/csv'
    )
else:
    st.warning("분석할 데이터가 없습니다. 원본 파일을 확인해주세요.")