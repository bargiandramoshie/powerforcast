import streamlit as st
import requests
from datetime import datetime
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
    
    # 日期选择（3月1日到4月30日）
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
# 图1：回测3线图（直接嵌入Kaggle生成的HTML）
# ============================================================
st.header("📈 回测准确率（2026年3月-4月）")

backtest_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/backtest_3lines.html"
try:
    response = requests.get(backtest_url)
    if response.status_code == 200:
        # 直接嵌入原始HTML，保留Kaggle生成的样式
        st.components.v1.html(response.text, height=550)
    else:
        st.info("回测图表生成中，请先在Kaggle运行Cell 2和Cell 3")
except:
    st.info("正在加载回测图表...")

# ============================================================
# 图2：预测图（直接嵌入Kaggle生成的HTML）
# ============================================================
st.header(f"📊 {selected_date.strftime('%Y-%m-%d')} 电价预测")

# 注意：prediction_2lines.html 是固定日期的，需要根据选择的日期动态获取
# 目前先用最新预测图，后续可以按日期命名多个文件
prediction_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/reports/prediction_2lines.html"
try:
    response = requests.get(prediction_url)
    if response.status_code == 200:
        st.components.v1.html(response.text, height=550)
    else:
        st.info("预测图表生成中，请先在Kaggle运行Cell 2和Cell 3")
except:
    st.info("正在加载预测图表...")

st.caption("⚡ 数据来源：贵州电力市场 | 模型准确率 75.3% | 图表由Kaggle生成")
