import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import requests
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="电力市场预测", page_icon="⚡", layout="wide")

st.title("⚡ 贵州电力市场价差预测系统")
st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.header("📅 查询设置")
    
    date_range = pd.date_range('2026-03-01', '2026-04-30', freq='D')
    selected_date = st.selectbox(
        "选择预测日期",
        options=date_range,
        format="YYYY-MM-DD",
        index=len(date_range) - 1
    )
    
    st.markdown("---")
    st.header("📊 模型信息")
    st.metric("模型准确率", "75.3%")
    st.progress(0.753, text="75.3% / 83%目标")

# ============================================================
# 图1：回测3线图（嵌入HTML）
# ============================================================
st.header("📈 回测准确率（2026年3月-4月）")

backtest_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/backtest_3lines.html"
try:
    response = requests.get(backtest_url)
    if response.status_code == 200:
        st.components.v1.html(response.text, height=550)
    else:
        st.info("回测图表生成中，请先运行Kaggle Cell 2")
except:
    st.info("正在生成回测图表...")

# ============================================================
# 图2：根据选择的日期显示对应的预测图
# ============================================================
st.header(f"📊 {selected_date.strftime('%Y-%m-%d')} 电价预测")

# 根据选择的日期构建URL
prediction_url = f"https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/prediction_{selected_date.strftime('%Y-%m-%d')}.html"

try:
    response = requests.get(prediction_url)
    if response.status_code == 200:
        st.components.v1.html(response.text, height=550)
    else:
        # 如果该日期的文件不存在，显示提示
        st.info(f"暂无 {selected_date.strftime('%Y-%m-%d')} 的预测数据，请在Kaggle中生成")
except:
    st.info("预测数据加载中...")

st.caption("⚡ 数据来源：贵州电力市场 | 模型准确率 75.3%")
