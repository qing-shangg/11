import pandas as pd
import streamlit as st

# ----------------- ページ設定 -----------------
st.set_page_config(page_title="金沢公共施設ガイド", layout="wide")
st.title("🏛️ 金沢公共施設ガイド")

# ----------------- データ読込 -----------------
@st.cache_data
def load_data():
    df = pd.read_csv("processed_facilities.csv")

    # 列名の前後に付いた空白・改行を削除しておく（KeyError 回避）
    df.columns = df.columns.str.strip()

    return df

df = load_data()

# ----------------- 分類列を自動検出 -----------------
CANDIDATE_CLASS_COLS = ["施設分類", "POIコード", "名称_通称", "名称"]

class_col = next((c for c in CANDIDATE_CLASS_COLS if c in df.columns), None)

# ----------------- サイドバー UI -----------------
with st.sidebar:
    st.header("🔍 検索条件")

    # 施設タイプ選択
    if class_col:
        type_options = ["全て"] + sorted(df[class_col].dropna().unique().tolist())
        selected_type = st.selectbox(f"分類（{class_col}）を選択", type_options)
    else:
        st.info("分類用の列が見つかりませんでした。フィルタは省略します。")
        selected_type = "全て"

    # reviews があれば最小レビュー数フィルタ
    if "reviews" in df.columns:
        max_rev = int(df["reviews"].max())
        min_reviews = st.slider("最小レビュー数", 0, max_rev, 10)
    else:
        min_reviews = None

# ----------------- データフィルタ -----------------
filtered = df.copy()

if class_col and selected_type != "全て":
    filtered = filtered[filtered[class_col] == selected_type]

if min_reviews is not None:
    filtered = filtered[filtered["reviews"] >= min_reviews]

# ----------------- 地図描画 -----------------
# 緯度・経度 → lat/lon に揃えて st.map に渡す
if {"緯度", "経度"}.issubset(filtered.columns):
    geo = filtered.rename(columns={"緯度": "lat", "経度": "lon"})
    st.map(geo)
else:
    st.warning("緯度（緯度）と経度（経度）が無いので地図を表示できません。")

# ----------------- 表示 -----------------
st.subheader("📋 絞り込まれた施設一覧")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# --- デバッグ用：列名を確認したい場合はコメントアウトを外す ---
# st.write("列名一覧:", df.columns.tolist())
