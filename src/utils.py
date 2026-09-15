import pandas as pd
import os

def load_market_data(file_path: str = "data/sample_market_data.csv") -> pd.DataFrame:
    """
    Loads and preprocesses the market data CSV file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}. Please generate it first.")
    
    df = pd.read_csv(file_path)
    
    # Ensure Timestamp is correctly formatted
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
    return df
