import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#---------------------------------------------------------------------------------------

# 데이터 불러오기 ---（完）
# baci_hs = pd.read_csv("./file/BACI_HS22_Y2023_V202501.csv")

# 'i' 컬럼이 410인 데이터만 남기고 삭제 후 새 파일 생성 ---（完）
# baci_kor = baci_hs[baci_hs["i"] == 410 ].copy()
# baci_kor.to_csv("./file/baci_korea_only.csv", index = False) 

#---------------------------------------------------------------------------------------

# 데이터 불러오기
baci_korea = pd.read_csv("./file/baci_korea_only.csv")
country_codes = pd.read_csv("./file/country_codes_V202501.csv")

# 'k' 컬럼이 852352인 데이터만 추출 (반도체 매체 - 스마트카드)
baci_85 = baci_korea[baci_korea["k"] == 852352].copy()

#---------------------------------------------------------------------------------------

# country_codes 파일의 'country_code' 컬럼 이름을 j로 변경
country_codes = country_codes.rename(columns = {"country_code" : "j"})

# 'j' 컬럼을 매핑 - baci_korea 기준으로 country_codes의 정보를 옆으로 붙인다
baci_merged = pd.merge(baci_korea, country_codes, on = "j", how = "left")

# 필요한 컬럼만 선택 및 순서 재배치
baci_merged = baci_merged[["t", "i", "country_name", "k", "v", "q"]]

# "j" 컬럼에 국가 코드 대신 국가 이름 대입
baci_merged = baci_merged.rename(columns = {"country_name" : "j"})

#---------------------------------------------------------------------------------------

# 2023년밖에 없는 데이터를 2020~2023년 범위에서 랜덤으로 변경
baci_merged["t"] = np.random.randint(2020, 2024, size=len(baci_merged))
print(baci_merged.head())

#---------------------------------------------------------------------------------------

# 1. 연도별 수출액 합계
# 't'별로 그룹을 묶고 'v' 컬럼의 합계 구하기
yearly_total = baci_merged.groupby("t")["v"].sum().reset_index()
yearly_total_columns = ["Year", "Total_Value"]

# 2. 국가별 수출액 합계
# 'j'별로 그룹을 묶고 'v' 컬럼의 합계 구하기
country_total = baci_merged.groupby("j")["v"].sum().reset_index()
country_total.columns = ["Country", "Total_Value"]
country_total = country_total.sort_values(by = "Total_Value", ascending = False)

#---------------------------------------------------------------------------------------

# 그래프 시각화 (히트맵) - 상위
top_10_countries = country_total.head(10)["Country"].tolist()
baci_top10 = baci_merged[baci_merged["j"].isin(top_10_countries)]

# 피벗 테이블 생성 (행: 국가, 열: 연도, 값: 수출액 합계)
pivot_df = baci_top10.pivot_table(index="j", columns="t", values="v", aggfunc="sum")

plt.figure(figsize=(10, 6))
sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title("Yearly Export Value Heatmap (Product: 852352)", fontsize=14)
plt.show()

# 결과 출력
print("--- 연도별 합계 ---")
print(yearly_total)
print("\n--- 국가별 합계 (상위 5개국) ---")
print(country_total.head(5))