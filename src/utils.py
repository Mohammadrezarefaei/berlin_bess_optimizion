import pandas as pd
import numpy as np
import os

def load_market_data(file_path: str = "data/sample_market_data.csv") -> pd.DataFrame:
    """
    Loads and preprocesses the market data CSV file. 
    If the file is missing or empty, it automatically generates default sample data.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Check if file exists and is not empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        # Auto-generate sample data if empty or missing
        np.random.seed(42)
        timestamps = pd.date_range(start="2026-09-15 00:00:00", periods=24, freq="h")
        da_prices = np.random.uniform(20, 100, 24)
        cap_prices = np.random.uniform(5, 30, 24)
        da_prices[19] = 740.0  # Spike
        
        df_market = pd.DataFrame({
            "Timestamp": timestamps,
            "DA_Price": np.round(da_prices, 2),
            "Capacity_Price": np.round(cap_prices, 2)
        })
        df_market.to_csv(file_path, index=False)
    
    df = pd.read_csv(file_path)
    
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
    return df
