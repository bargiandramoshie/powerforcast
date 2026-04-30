import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="电力市场预测", page_icon="⚡", layout="wide")

st.title("⚡ 贵州电力市场价差预测系统")
st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================
# 从GitHub读取Kaggle生成的图表
# ============================================================

st.header("📈 双模型回测准确率对比")

# 嵌入HTML图表
backtest_html_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/backtest_accuracy.html"
st.components.v1.html(
    f"""
    <iframe src="{backtest_html_url}" width="100%" height="600" frameborder="0"></iframe>
    """,
    height=620
)

st.header("🔮 预测图表")

prediction_html_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/prediction_latest.html"
st.components.v1.html(
    f"""
    <iframe src="{prediction_html_url}" width="100%" height="850" frameborder="0"></iframe>
    """,
    height=870
)

# ============================================================
# 显示模型准确率
# ============================================================
st.sidebar.header("📊 模型信息")
st.sidebar.metric("全量模型准确率", "75.3%")
st.sidebar.metric("下午时段模型准确率", "86.7%")
st.sidebar.progress(86.7 / 100, text="86.7% / 83%目标")

st.caption("⚡ 图表由Kaggle模型自动生成，数据来源：贵州电力市场")
