# 🔋 German BESS Co-Optimization Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://berlinbeappptimizion-appqbldlvi4w5qdepf3vkbn.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, high-performance Mixed-Integer Linear Programming (MILP) co-optimization engine designed for Battery Energy Storage Systems (BESS) participating simultaneously in the German **Day-Ahead (DA)** and secondary reserve (**aFRR capacity**) markets.

---

## 🚀 Live Demo
Explore the interactive web application deployed on Streamlit Cloud:  
👉 **[Open BESS Co-Optimization Dashboard](https://berlinbeappptimizion-appqbldlvi4w5qdepf3vkbn.streamlit.app/)**

---

## 📊 Key Features
- **Simultaneous Revenue Stacking**: Co-optimizes energy arbitrage in the Day-Ahead spot market with capacity reservation payments in the aFRR balancing market.
- **Advanced MILP Formulation**: Built using Python and optimized via the CBC solver, strictly enforcing physical battery constraints, state-of-charge (SoC) dynamics, and simultaneous power/reserve boundaries.
- **Robust Data Pipeline**: Features automated in-memory fallback mechanisms to gracefully handle missing or empty dataset inputs without crashing.
- **Dark-Mode UI/UX**: Designed with a professional dark aesthetic, custom HTML/CSS metric cards, and dynamic Plotly visualizations featuring customized tooltips and legends.

---

## 🛠️ Tech Stack
- **Core Optimization**: Python, PuLP (MILP Modeling), CBC Solver
- **Data Manipulation**: Pandas, NumPy
- **Data Visualization**: Plotly (Subplots, Interactive Dashboards)
- **Web Framework**: Streamlit

---

## ⚙️ Mathematical Formulation (Overview)
The optimization model maximizes total revenue over a 24-hour horizon:

$$\max \sum_{t} \left( \text{Discharge}_{t} \cdot \pi^{\text{DA}}_t - \text{Charge}_{t} \cdot \pi^{\text{DA}}_t + \text{Reserve}_{t} \cdot \pi^{\text{aFRR}}_t \right)$$

Subject to:
1. **Power Limits**: Total power allocated to charging, discharging, and aFRR reserves cannot exceed the inverter's maximum power rating.
2. **SoC Dynamics**: Tracking battery energy content accounting for round-trip efficiency ($\eta$).
3. **Mutual Exclusivity / Operational Integrity**: Preventing simultaneous high-intensity conflicting states where physically constrained.

---

## 🗂️ Project Structure
```text
berlin_bess_optimizer/
│
├── app.py                  # Main Streamlit dashboard application
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
├── data/
│   └── sample_market_data.csv  # 24-hour DA and aFRR price profiles
└── src/
    ├── __init__.py
    ├── engine_milp.py      # MILP co-optimization mathematical model
    └── utils.py            # Robust data loading and in-memory fallbacks
