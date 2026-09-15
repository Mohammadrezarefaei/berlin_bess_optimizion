import pytest
import pandas as pd
import numpy as np
from src.engine_milp import BESS_CoOptimizer

@pytest.fixture
def extreme_data():
    """Generates 24 hours of highly volatile market data."""
    np.random.seed(100)
    return pd.DataFrame({
        'DA_Price': np.random.uniform(-100, 1000, 24), # Includes negative prices & massive spikes
        'Capacity_Price': np.random.uniform(0, 100, 24)
    })

def test_soc_bounds_extreme_prices(extreme_data):
    """
    Ensures State of Charge (SoC) never violates capacity bounds (0 <= SoC <= Max).
    Tested under extreme price conditions which might lure the solver.
    """
    cap_mwh = 10.0
    optimizer = BESS_CoOptimizer(capacity_mwh=cap_mwh, max_power_mw=5.0)
    optimized_df = optimizer.optimize(extreme_data)
    
    # Assert SoC never goes below zero
    assert optimized_df['Optimized_SoC_MWh'].min() >= -1e-6, "SoC became negative!"
    
    # Assert SoC never exceeds battery capacity
    assert optimized_df['Optimized_SoC_MWh'].max() <= cap_mwh + 1e-6, f"SoC exceeded {cap_mwh} MWh!"

def test_no_simultaneous_charge_discharge(extreme_data):
    """
    Ensures that BESS does not charge and discharge in the same hour.
    While MILP might sometimes find a loop-hole, business logic disallows it.
    """
    optimizer = BESS_CoOptimizer(capacity_mwh=10.0, max_power_mw=5.0)
    optimized_df = optimizer.optimize(extreme_data)
    
    # A product of charge and discharge should be close to zero at every timestep
    simultaneous_action = (optimized_df['Optimized_Charge_MW'] > 0.1) & \
                          (optimized_df['Optimized_Discharge_MW'] > 0.1)
    
    assert not simultaneous_action.any(), "Simultaneous charge and discharge detected!"
