import pandas as pd
import streamlit as st

st.set_page_config(page_title="金沢公共施設ガイド", layout="wide")
st.title("🏛️ 金沢公共施設ガイド")

@st.cache_data
def load_data():
    return pd.read_csv("processed_facilities.csv")

df = load_data()

# -------- サイドバー --------
with st.sidebar:
    st.header("🔍 検索条件")

    # ① 设施分类列判断
    if "施設分類" in df.columns:
        type_col = "施設分類"
    else:
        type_col = "POIコード"          # 退而用 POI コード

    types = ["全て"] + sorted(df[type_col].dropna().unique().tolist())
    selected_type = st.selectbox("施設タイプを選択", types)

    # ② reviews 列判断
    if "reviews" in df.columns:
        max_review = int(df["reviews"].max())
        min_reviews = st.slider("最小レビュー数", 0, max_review, 10)
    else:
        min_reviews = None  # 不显示 slider

# -------- フィルタ --------
filtered = df.copy()
if selected_type != "全て":
    filtered = filtered[filtered[type_col] == selected_type]

if min_reviews is not None:
    filtered = filtered[filtered["reviews"] >= min_reviews]

# -------- 地図 --------
if {"緯度", "経度"}.issubset(filtered.columns):
    geo = filtered.rename(columns={"緯度": "lat", "経度": "lon"})
    st.map(geo)
else:
    st.warning("データに緯度・経度列が見つかりません。地図は表示されません。")

# -------- 表 --------
st.subheader("📋 絞り込まれた施設一覧")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

