import pandas as pd
import numpy as np

def load_market_data(file_path: str = "data/sample_market_data.csv") -> pd.DataFrame:
    """
    Loads market data safely. If the file is missing or empty, 
    it generates the standard German market simulation profile in memory.
    """
    try:
        # Try reading the file normally
        df = pd.read_csv(file_path)
        if df.empty or 'DA_Price' not in df.columns:
            raise ValueError("File is empty or malformed.")
    except Exception:
        # Fallback: In-memory generation if file is missing/empty
        np.random.seed(42)
        timestamps = pd.date_range(start="2026-09-15 00:00:00", periods=24, freq="h")
        da_prices = np.random.uniform(20, 100, 24)
        cap_prices = np.random.uniform(5, 30, 24)
        da_prices[19] = 740.0  # The famous spike
        
        df = pd.DataFrame({
            "Timestamp": timestamps,
            "DA_Price": np.round(da_prices, 2),
            "Capacity_Price": np.round(cap_prices, 2)
        })
    
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
    return df
