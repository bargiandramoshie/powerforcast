import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="贵州电力市场预测系统",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("⚡ 贵州电力市场价差预测系统")
st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================
# 数据（你每次更新这里即可）
# ============================================================

# 模型准确率
MODEL_ACCURACY = {
    'afternoon': 86.7,
    'full': 75.7,
    'target': 83
}

# 下午时段预测数据（每次Kaggle跑完后更新这里）
PREDICTION_DATA = {
    13: {'da_price': 380, 'rt_price': 405, 'spread': 25, 'coefficient': 1.02, 'action': '买入', 'confidence': 85},
    14: {'da_price': 385, 'rt_price': 420, 'spread': 35, 'coefficient': 1.05, 'action': '买入', 'confidence': 92},
    15: {'da_price': 390, 'rt_price': 432, 'spread': 42, 'coefficient': 1.08, 'action': '强烈买入', 'confidence': 95},
    16: {'da_price': 388, 'rt_price': 408, 'spread': 20, 'coefficient': 1.02, 'action': '买入', 'confidence': 80}
}

# 回测数据（2026年3月-4月）
@st.cache_data
def get_backtest_data():
    dates = pd.date_range('2026-03-01', '2026-04-28', freq='D')
    # 模拟数据（实际可从CSV读取）
    afternoon_data = [75,82,78,85,88,92,86,95,89,84,79,87,91,83,81,86,93,88,82,87,92,90,85,80,89,94,91,86,84,90,88,85,81,89,93,87,83,79,96,89,84,82,87,91,85,83,88,92,90,86,84,89,94,91,87,85,90,88,93]
    full_data = [68,72,65,70,75,78,73,80,76,72,68,74,77,71,69,73,79,75,70,74,78,76,72,69,75,80,77,73,71,76,74,72,68,75,79,73,70,66,82,76,71,69,74,78,72,70,75,79,77,73,71,76,80,78,74,72,77,75,79]
    
    return pd.DataFrame({
        'date': dates,
        'full_model': [f/100 for f in full_data[:len(dates)]],
        'afternoon_model': [a/100 for a in afternoon_data[:len(dates)]]
    })

BACKTEST_DATA = get_backtest_data()

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.header("📅 查询设置")
    
    query_date = st.date_input(
        "选择预测日期",
        value=datetime(2026, 4, 30).date(),
        min_value=datetime(2026, 4, 1).date(),
        max_value=datetime(2026, 5, 31).date()
    )
    
    st.markdown("---")
    st.header("📊 模型准确率")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("下午时段模型", f"{MODEL_ACCURACY['afternoon']}%", 
                  delta=f"+{MODEL_ACCURACY['afternoon'] - MODEL_ACCURACY['target']:.1f}%")
    with col2:
        st.metric("24小时模型", f"{MODEL_ACCURACY['full']}%")
    
    st.progress(MODEL_ACCURACY['afternoon'] / 100, text=f"目标 {MODEL_ACCURACY['target']}%")
    
    st.markdown("---")
    st.caption("数据范围: 2025-09-01 ~ 2026-04-28")

# ============================================================
# Tab 1: 回测分析 - 3线图
# ============================================================
tab1, tab2, tab3 = st.tabs(["📈 回测分析", "🔮 价格预测", "💰 交易策略"])

with tab1:
    st.header("📈 每日准确率回测")
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=BACKTEST_DATA['date'], y=BACKTEST_DATA['full_model'] * 100,
        mode='lines+markers', name='24小时全量模型',
        line=dict(color='#3498db', width=2), marker=dict(size=4)
    ))
    
    fig1.add_trace(go.Scatter(
        x=BACKTEST_DATA['date'], y=BACKTEST_DATA['afternoon_model'] * 100,
        mode='lines+markers', name='下午时段专用模型',
        line=dict(color='#e67e22', width=2.5), marker=dict(size=5)
    ))
    
    fig1.add_hline(y=83, line_dash="dash", line_color="red", 
                   annotation_text="83%目标", annotation_position="bottom right")
    
    avg_afternoon = BACKTEST_DATA['afternoon_model'].mean() * 100
    fig1.add_hline(y=avg_afternoon, line_dash="dot", line_color="orange",
                   annotation_text=f"下午平均={avg_afternoon:.1f}%", annotation_position="top left")
    
    fig1.update_layout(
        title="每日方向预测准确率（2026年3月-4月）",
        xaxis_title="日期",
        yaxis_title="准确率 (%)",
        yaxis_range=[50, 100],
        hovermode='x unified',
        height=450
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("下午模型平均", f"{BACKTEST_DATA['afternoon_model'].mean()*100:.1f}%")
    with col2:
        st.metric("下午模型最高", f"{BACKTEST_DATA['afternoon_model'].max()*100:.1f}%")
    with col3:
        st.metric("下午模型最低", f"{BACKTEST_DATA['afternoon_model'].min()*100:.1f}%")
    with col4:
        high_days = (BACKTEST_DATA['afternoon_model'] >= 0.83).sum()
        st.metric("达标天数", f"{high_days}/{len(BACKTEST_DATA)}")

# ============================================================
# Tab 2: 价格预测 - 2线图
# ============================================================
with tab2:
    st.header(f"🔮 {query_date} 下午时段电价预测")
    
    hours = list(PREDICTION_DATA.keys())
    da_prices = [PREDICTION_DATA[h]['da_price'] for h in hours]
    rt_prices = [PREDICTION_DATA[h]['rt_price'] for h in hours]
    spreads = [PREDICTION_DATA[h]['spread'] for h in hours]
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=hours, y=da_prices,
        mode='lines+markers', name='日前电价',
        line=dict(color='#3498db', width=3), marker=dict(size=10, symbol='circle')
    ))
    
    fig2.add_trace(go.Scatter(
        x=hours, y=rt_prices,
        mode='lines+markers', name='预测实时电价',
        line=dict(color='#e74c3c', width=3, dash='dash'), marker=dict(size=10, symbol='diamond')
    ))
    
    fig2.update_layout(
        title=f"{query_date} 下午时段电价预测",
        xaxis_title="小时",
        yaxis_title="电价 (元/MWh)",
        xaxis=dict(tickmode='array', tickvalues=hours, ticktext=[f'{h}:00' for h in hours]),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 预测表格
    pred_df = pd.DataFrame([
        {'时段': f"{h}:00", '日前价': PREDICTION_DATA[h]['da_price'], 
         '预测实时价': PREDICTION_DATA[h]['rt_price'], 
         '价差': f"+{PREDICTION_DATA[h]['spread']}",
         '置信度': f"{PREDICTION_DATA[h]['confidence']}%"}
        for h in hours
    ])
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

# ============================================================
# Tab 3: 交易策略 - 申报系数柱状图
# ============================================================
with tab3:
    st.header("💰 交易策略与申报建议")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 申报系数建议")
        
        coefficients = [PREDICTION_DATA[h]['coefficient'] for h in hours]
        colors = ['#2ecc71' if c > 1.03 else '#f39c12' if c > 1.0 else '#e74c3c' for c in coefficients]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=[f"{h}:00" for h in hours], y=coefficients,
            marker_color=colors,
            text=[f"{c:.2f}" for c in coefficients],
            textposition='outside'
        ))
        fig3.add_hline(y=1.0, line_dash="solid", line_color="gray")
        fig3.update_layout(
            title="各时段申报系数建议",
            xaxis_title="时段",
            yaxis_title="申报系数",
            yaxis_range=[0.9, 1.15],
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.subheader("🎯 系数说明")
        st.info("""
        - **1.08**：强烈买入
        - **1.05**：建议买入
        - **1.02**：谨慎买入
        - **1.00**：观望
        """)
    
    # 操作建议表格
    advice_df = pd.DataFrame([
        {'时段': f"{h}:00-{h+1}:00", '日前价': PREDICTION_DATA[h]['da_price'],
         '预期价差': f"+{PREDICTION_DATA[h]['spread']}",
         '申报系数': f"{PREDICTION_DATA[h]['coefficient']:.2f}",
         '操作建议': PREDICTION_DATA[h]['action'],
         '置信度': f"{PREDICTION_DATA[h]['confidence']}%"}
        for h in hours
    ])
    st.dataframe(advice_df, use_container_width=True, hide_index=True)
    
    # 策略总结
    total_return = sum(PREDICTION_DATA[h]['spread'] for h in hours)
    st.success(f"💰 预期总收益：+{total_return} 元/MWh")
    st.warning("⚠️ 风险提示：节假日期间波动较大，建议减仓")

# ============================================================
# 底部
# ============================================================
st.markdown("---")
st.caption("⚡ 数据来源：贵州电力市场 | 下午时段模型准确率 86.7%")
