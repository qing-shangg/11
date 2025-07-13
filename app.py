import pandas as pd
import streamlit as st

# 设置页面
st.set_page_config(layout="wide")
st.title("🏛️ 金沢公共施設ガイド")

# 加载数据
@st.cache_data
def load_data():
    return pd.read_csv("facilities_processed.csv")

df = load_data()

# 侧边栏筛选器
with st.sidebar:
    st.header("検索条件")
    selected_type = st.selectbox(
        "施設タイプ",
        ["全て"] + list(df['施設分類'].unique())
    )
    min_reviews = st.slider("最小レビュー数", 0, 300, 50)

# 数据过滤
if selected_type != "全て":
    df = df[df['施設分類'] == selected_type]
df = df[df['reviews'] >= min_reviews]

# 显示结果
st.map(df)  # 自动显示地图！
st.write(df)  # 显示表格