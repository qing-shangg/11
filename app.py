import pandas as pd
import streamlit as st
from io import StringIO

# ---------------- ページ設定 ----------------
st.set_page_config(page_title="金沢公共施設マップ", layout="wide")
st.title("🏛️ 金沢公共施設マップ")

# ---------------- データ読込 ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("processed_facilities.csv")
    df.columns = df.columns.str.strip()  # 列名前后空白去除
    return df

df = load_data()

# ---------------- 列存在チェック ----------------
def col_exists(col):
    return col in df.columns

# ---------------- サイドバー ----------------
with st.sidebar:
    st.header("🔍 検索・絞り込み")

    # キーワード検索
    keyword = st.text_input("キーワード検索（名称/通称）", placeholder="例）文化、図書館、体育館")

    # POIコードで絞る
    if col_exists("POIコード"):
        poi_options = sorted(df["POIコード"].dropna().unique().tolist())
        selected_pois = st.multiselect("POIコードでフィルター", poi_options)
    else:
        selected_pois = []
        st.caption("⚠️ POIコード列が存在しないためフィルター不可")

# ---------------- データフィルタ ----------------
filtered = df.copy()

# キーワードフィルタ（名称 & 名称_通称）
if keyword:
    conditions = []
    if col_exists("名称"):
        conditions.append(filtered["名称"].astype(str).str.contains(keyword, case=False, na=False))
    if col_exists("名称_通称"):
        conditions.append(filtered["名称_通称"].astype(str).str.contains(keyword, case=False, na=False))
    if conditions:
        combined = conditions[0]
        for cond in conditions[1:]:
            combined |= cond
        filtered = filtered[combined]
    else:
        st.warning("⚠️ 検索対象の列（名称/通称）が見つかりません。")

# POIコードフィルタ
if selected_pois and col_exists("POIコード"):
    filtered = filtered[filtered["POIコード"].isin(selected_pois)]

# ---------------- 地図表示 ----------------
if col_exists("緯度") and col_exists("経度"):
    map_df = filtered.rename(columns={"緯度": "latitude", "経度": "longitude"}).copy()

    # ❗ 只保留数值类型的经纬度，删除空值或非法字符
    map_df["latitude"] = pd.to_numeric(map_df["latitude"], errors="coerce")
    map_df["longitude"] = pd.to_numeric(map_df["longitude"], errors="coerce")
    map_df = map_df.dropna(subset=["latitude", "longitude"])

    if not map_df.empty:
        st.map(map_df)
    else:
        st.info("📍 フィルタ後、有効な緯度・経度が含まれていないため、地図を表示できません。")
else:
    st.info("⚠️ 緯度・経度の列が見つかりません。地図は非表示になります。")

# ---------------- CSV ダウンロード ----------------
csv_buffer = StringIO()
filtered.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 絞り込み結果をCSVでダウンロード",
    data=csv_buffer.getvalue(),
    file_name="filtered_facilities.csv",
    mime="text/csv",
    use_container_width=True
)
