import pandas as pd
import streamlit as st

# 设置页面信息
st.set_page_config(page_title="金沢公共施設ガイド", layout="wide")
st.title("🏛️ 金沢公共施設ガイド")

# 数据加载函数（使用 Streamlit 缓存）
@st.cache_data
def load_data():
    return pd.read_csv("processed_facilities.csv")

# 读取数据
df = load_data()

# 侧边栏：筛选条件
with st.sidebar:
    st.header("🔍 検索条件")
    
    # 选择设施分类
    facility_types = ["全て"] + sorted(df["施設分類"].dropna().unique().tolist())
    selected_type = st.selectbox("施設タイプを選択", facility_types)
    
    # 设置最小レビュー数
    max_review = int(df["reviews"].max())
    min_reviews = st.slider("最小レビュー数", 0, max_review, 10)

# 数据筛选
filtered_df = df.copy()
if selected_type != "全て":
    filtered_df = filtered_df[filtered_df["施設分類"] == selected_type]
filtered_df = filtered_df[filtered_df["reviews"] >= min_reviews]

# 地图显示（需要经纬度）
if {"lat", "lon"}.issubset(filtered_df.columns):
    st.map(filtered_df.rename(columns={"lat": "latitude", "lon": "longitude"}))
else:
    st.warning("地図を表示するために、緯度（lat）と経度（lon）の列が必要です。")

# 表格展示
st.subheader("📋 絞り込まれた施設一覧")
st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
