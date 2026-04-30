import pandas as pd
import glob
import re
import os

def parse_cell(val):
    if pd.isna(val) or val == "" or val == "-":
        return 0, 0, 0.0
    match = re.search(r"(\d+)/(\d+)\(([\d\.]+)\)", str(val))
    if match:
        return int(match.group(1)), int(match.group(2)), float(match.group(3))
    match_simple = re.search(r"(\d+)/(\d+)", str(val))
    if match_simple:
        return int(match_simple.group(1)), int(match_simple.group(2)), 0.0
    return 0, 0, 0.0

def process_files():
    all_data = []
    file_list = glob.glob("data/*.csv") # data 폴더 안의 csv 파일들
    
    if not file_list:
        print("에러: data 폴더 안에 CSV 파일이 없습니다!")
        return

    for file in file_list:
        year = re.search(r'\d{4}', os.path.basename(file)).group()
        df = pd.read_csv(file, skiprows=2) 
        df = df.dropna(subset=['교과'])
        df_melted = df.melt(id_vars=['교과'], var_name='지역', value_name='원본값')
        df_melted['연도'] = year
        parsed_results = df_melted['원본값'].apply(parse_cell)
        df_melted[['배치', '지원', '커트라인']] = pd.DataFrame(parsed_results.tolist(), index=df_melted.index)
        all_data.append(df_melted)
        print(f"{year}년 데이터 처리 완료")

    total_df = pd.concat(all_data, ignore_index=True)
    total_df.to_csv("total_data.csv", index=False, encoding="utf-8-sig")
    print("--- 성공: total_data.csv 파일이 생성되었습니다! ---")

if __name__ == "__main__":
    process_files()