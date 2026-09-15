import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import internal modules
from src.engine_milp import BESS_CoOptimizer
from src.utils import load_market_data

# --- PAGE CONFIG ---
st.set_page_config(page_title="BESS Co-Optimization Engine", layout="wide")

# --- CUSTOM CSS FOR CARDS & PLOTS ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px 20px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-title {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value {
        color: #38bdf8 !important;
        font-size: 24px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔋 German BESS Co-Optimization Engine")
st.markdown("A demonstration of MILP-based co-optimization for Day-Ahead and aFRR markets.")

# --- SIDEBAR ---
st.sidebar.header("Battery Constraints")
cap_mwh = st.sidebar.number_input("Capacity (MWh)", min_value=1.0, value=10.0, step=1.0)
power_mw = st.sidebar.number_input("Max Power (MW)", min_value=1.0, value=5.0, step=1.0)
efficiency = st.sidebar.slider("Round-Trip Efficiency", 0.7, 1.0, 0.9, step=0.01)

# --- LOAD DATA ---
try:
    df_market = load_market_data("data/sample_market_data.csv")
except Exception as e:
    st.error(f"Error loading market data: {e}")
    st.stop()

# --- OPTIMIZATION ENGINE ---
if st.button("Run MILP Optimization", type="primary"):
    with st.spinner("Running CBC Solver..."):
        optimizer = BESS_CoOptimizer(capacity_mwh=cap_mwh, max_power_mw=power_mw, efficiency=efficiency)
        optimized_df = optimizer.optimize(df_market)
        
        st.success("Optimization Completed Successfully!")
        
        # --- FINANCIAL METRICS ---
        total_da_revenue = (optimized_df['Optimized_Discharge_MW'] * optimized_df['DA_Price']).sum() - \
                           (optimized_df['Optimized_Charge_MW'] * optimized_df['DA_Price']).sum()
        total_afrr_revenue = (optimized_df['Optimized_Reserve_MW'] * optimized_df['Capacity_Price']).sum()
        total_net = total_da_revenue + total_afrr_revenue
        
        # --- CUSTOM HTML METRIC CARDS ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Day-Ahead Revenue</div>
                    <div class="metric-value">€ {total_da_revenue:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">aFRR Capacity Revenue</div>
                    <div class="metric-value">€ {total_afrr_revenue:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Net Profit</div>
                    <div class="metric-value">€ {total_net:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- PLOTLY CHART ---
        st.subheader("24-Hour Dispatch Profile")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        hours = optimized_df.index.tolist()

        fig.add_trace(go.Bar(x=hours, y=optimized_df['Optimized_Charge_MW'], name="Charge (MW)", marker_color='#00CC96'), secondary_y=False)
        fig.add_trace(go.Bar(x=hours, y=-optimized_df['Optimized_Discharge_MW'], name="Discharge (MW)", marker_color='#EF553B'), secondary_y=False)
        fig.add_trace(go.Bar(x=hours, y=optimized_df['Optimized_Reserve_MW'], name="aFRR Reserve (MW)", marker_color='#AB63FA'), secondary_y=False)
        
        fig.add_trace(go.Scatter(x=hours, y=optimized_df['DA_Price'], name="DA Price (€/MWh)", line=dict(color='#FFA15A', dash='dot')), secondary_y=True)

        fig.update_layout(
            template="plotly_dark", 
            barmode='relative', 
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                bgcolor="rgba(30, 41, 59, 0.9)",
                bordercolor="#334155",
                borderwidth=1,
                font=dict(color="#38bdf8")
            ),
            hoverlabel=dict(
                bgcolor="#1e293b",
                bordercolor="#334155",
                font=dict(family="sans-serif", size=12, color="#38bdf8")  # تنظیم رنگ و فونت متن داخل هاور
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- DATA TABLE ---
        st.subheader("Optimization Results Data")
        st.dataframe(optimized_df.style.highlight_max(axis=0))
