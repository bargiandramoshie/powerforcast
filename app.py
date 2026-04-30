import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import requests
import joblib
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="电力市场预测", page_icon="⚡", layout="wide")
st.title("⚡ 贵州电力市场价差预测系统")

# ============================================================
# 1. 加载模型（从 GitHub 下载，并缓存）
# ============================================================
@st.cache_resource
def load_model():
    """从GitHub下载并加载模型和scaler"""
    model_url = "https://github.com/bargiandramoshie/powerforcast/raw/main/models/full_model.pkl"
    scaler_url = "https://github.com/bargiandramoshie/powerforcast/raw/main/models/scaler.pkl"
    
    try:
        model_response = requests.get(model_url)
        scaler_response = requests.get(scaler_url)
        
        if model_response.status_code == 200 and scaler_response.status_code == 200:
            model = joblib.load(BytesIO(model_response.content))
            scaler = joblib.load(BytesIO(scaler_response.content))
            st.success("✅ 模型加载成功")
            return model, scaler
        else:
            st.error("❌ 模型文件下载失败，请检查 GitHub 文件是否存在")
            return None, None
    except Exception as e:
        st.error(f"❌ 模型加载出错: {e}")
        return None, None

# ============================================================
# 2. 获取日前电价（从原始数据文件）
# ============================================================
@st.cache_data
def get_da_price(target_date):
    """从GitHub获取指定日期的日前电价"""
    data_url = "https://raw.githubusercontent.com/bargiandramoshie/powerforcast/main/data/4-251.xlsx"
    try:
        # 注意：这里需要一个可公开访问的原始数据文件，可能需要你手动上传一次
        df = pd.read_excel(data_url, sheet_name='日前交易电价')
        df['hour'] = df['时间点'].str.split(':').str[0].astype(int)
        df['date'] = pd.to_datetime(df['日期']).dt.date
        price_dict = df[df['date'] == target_date].set_index('hour')['电价_元每兆瓦时'].to_dict()
        return price_dict if price_dict else None
    except:
        # 如果真实数据获取失败，用一个模拟数据作为后备方案
        st.warning("无法获取真实日前电价，使用模拟数据演示。")
        base_price = 350
        return {h: base_price + 10 * np.sin(h / 24 * 2 * np.pi) for h in range(24)}

# ============================================================
# 3. 预测24小时价差
# ============================================================
def predict_spread(model, scaler, target_date):
    # 这里需要构造预测所需的特征，逻辑和你 Kaggle Cell 2 中一致。
    # 为了代码简洁，此处提供一个简化示例。实际使用时，你需要把完整的特征构造逻辑复制过来。
    # 由于特征构造比较复杂，这里先留一个占位，并返回模拟数据
    st.warning("预测功能开发中，当前显示模拟数据。")
    hours = list(range(24))
    da_prices = [get_da_price(target_date).get(h, 350) for h in hours]
    pred_spreads = [np.random.randint(-30, 60) for _ in hours]
    pred_rt_prices = [da_prices[i] + pred_spreads[i] for i in range(24)]
    return hours, da_prices, pred_rt_prices, pred_spreads

# ============================================================
# 4. 主界面
# ============================================================
model, scaler = load_model()

if model is not None:
    with st.sidebar:
        st.header("📅 查询设置")
        # 允许用户选择 2026年3月1日到4月30日之间的任何一天
        date_range = pd.date_range('2026-03-01', '2026-04-30', freq='D')
        selected_date = st.selectbox("选择预测日期", options=date_range, format="YYYY-MM-DD")
        st.markdown("---")
        st.header("📊 模型信息")
        st.metric("模型准确率", "75.3%")
        st.progress(0.753, text="75.3% / 83%目标")

    st.header(f"📊 {selected_date.strftime('%Y-%m-%d')} 电价预测")
    
    # 根据用户选择的日期进行预测
    hours, da_prices, pred_rt_prices, pred_spreads = predict_spread(model, scaler, selected_date.date())
    
    # 绘制2线图
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=da_prices, mode='lines+markers', name='日前电价', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=hours, y=pred_rt_prices, mode='lines+markers', name='预测实时电价', line=dict(color='red', width=3, dash='dash')))
    fig.update_layout(title='电价预测', xaxis_title='小时', yaxis_title='元/MWh', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # 绘制价差柱状图
    colors = ['#2ecc71' if s > 0 else '#e74c3c' for s in pred_spreads]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=hours, y=pred_spreads, marker_color=colors, text=[f"{s:+.0f}" for s in pred_spreads], textposition='outside'))
    fig2.add_hline(y=0, line_dash="solid", line_color="gray")
    fig2.update_layout(title='价差预测', xaxis_title='小时', yaxis_title='价差 (元/MWh)', height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    # 显示交易策略
    st.subheader("📋 交易策略")
    buy_hours = [f"{h:02d}:00" for h, s in zip(hours, pred_spreads) if s > 10]
    sell_hours = [f"{h:02d}:00" for h, s in zip(hours, pred_spreads) if s < -10]
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**建议买入**\n\n{', '.join(buy_hours) if buy_hours else '无'}")
    with col2:
        st.error(f"**建议卖出**\n\n{', '.join(sell_hours) if sell_hours else '无'}")
    st.info(f"💰 预期总收益: {sum(pred_spreads):+.0f} 元/MWh")

st.caption("⚡ 数据来源：贵州电力市场 | 模型准确率 75.3%")
