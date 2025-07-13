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
    df.columns = df.columns.str.strip()          # 余計な空白対策
    return df

df = load_data()

# ---------------- サイドバー ----------------
with st.sidebar:
    st.header("🔍 フィルタ")

    # キーワード検索（名称・通称）
    keyword = st.text_input("キーワード（名称・通称）で検索", placeholder="例）ホール / 美術館")

    # POIコードでの絞り込み（任意）
    if "POIコード" in df.columns:
        poi_options = sorted(df["POIコード"].dropna().unique().tolist())
        poi_selected = st.multiselect("POIコードで絞り込み（複数選択可）", poi_options)
    else:
        poi_selected = []

    # ダウンロードボタンを先に用意（後でデータを渡す）
    download_btn = st.empty()

# ---------------- データフィルタ ----------------
filtered = df.copy()

if keyword:
    # 名称・通称どちらにもヒットするように
    mask_name = filtered["名称"].fillna("").str.contains(keyword, case=False, na=False)
    mask_nickname = filtered["名称_通称"].fillna("").str.contains(keyword, case=False, na=False) \
                    if "名称_通称" in filtered.columns else False
    filtered = filtered[mask_name | mask_nickname]

if poi_selected:
    filtered = filtered[filtered["POIコード"].isin(poi_selected)]

# ---------------- 地図描画 ----------------
if {"緯度", "経度"}.issubset(filtered.columns):
    geo = filtered.rename(columns={"緯度": "latitude", "経度": "longitude"})
    st.map(geo)
else:
    st.warning("緯度・経度の列が見つからないため、地図を表示できません。")

# ---------------- 表示 ----------------
st.subheader(f"📋 施設一覧（{len(filtered)} 件）")

# 表示用に主要列だけ抽出；存在しない列はスキップ
display_cols = [c for c in ["名称", "名称_通称", "所在地_連結表記", "電話番号", "URL"] if c in filtered.columns]
st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True)

# ---------------- CSV ダウンロード ----------------
csv_buffer = StringIO()
filtered.to_csv(csv_buffer, index=False)
download_btn.download_button(
    label="📥 表示中のデータを CSV でダウンロード",
    data=csv_buffer.getvalue(),
    file_name="facilities_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

