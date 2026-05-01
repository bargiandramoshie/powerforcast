import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="电力市场预测", page_icon="⚡", layout="wide")

st.title("⚡ 贵州电力市场价差预测系统")
st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================
# 侧边栏 - 简化版，避免日期问题
# ============================================================
with st.sidebar:
    st.header("📅 查询设置")
    
    # 手动定义可选日期
    date_options = [
        '2026-04-28', '2026-04-29', '2026-04-30', 
        '2026-05-01', '2026-05-02', '2026-05-03'
    ]
    
    selected_date = st.selectbox(
        "选择预测日期",
        options=date_options,
        index=2  # 默认选中 2026-04-30
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
        st.info("回测图表加载中...")
except:
    st.info("正在加载回测图表")

# ============================================================
# 图2：根据选择的日期显示对应的预测图
# ============================================================
st.header(f"📊 {selected_date} 电价预测")

# 根据选择的日期构建URL
prediction_url = f"https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/prediction_{selected_date}.html"

try:
    response = requests.get(prediction_url)
    if response.status_code == 200:
        st.components.v1.html(response.text, height=550)
    else:
        st.info(f"📌 暂无 {selected_date} 的预测数据")
        st.markdown(f"""
        **请在 Kaggle 中运行 Cell 2 生成该日期的预测图：**
        
        1. 修改 Cell 2 中的 `TARGET_DATE = '{selected_date}'`
        2. 重新运行 Cell 2
        3. 运行 Cell 3 上传到 GitHub
        """)
except Exception as e:
    st.info(f"预测数据加载中...")

st.caption("⚡ 数据来源：贵州电力市场 | 模型准确率 75.3%")
