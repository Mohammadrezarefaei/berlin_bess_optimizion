import pytest
import pandas as pd
import numpy as np
from src.engine_milp import BESS_CoOptimizer

@pytest.fixture
def bess_params():
    """Returns standard BESS parameters."""
    return {"capacity_mwh": 10.0, "max_power_mw": 5.0}

def test_no_data_leakage_future_spikes(bess_params):
    """
    Ensures that a future price spike does not influence optimization
    decisions in previous time steps.
    
    Test scenario: Compare dispatch of a 'Normal' profile vs. a profile with
    an extreme price spike injected in the future. Decisions before the
    leakage hour must be identical.
    """
    optimizer = BESS_CoOptimizer(**bess_params)
    
    # 1. Create a baseline normal price profile (48 hours)
    np.random.seed(42)
    normal_data = pd.DataFrame({
        'DA_Price': np.random.uniform(30, 70, 48),
        'Capacity_Price': np.random.uniform(10, 20, 48)
    })
    
    # 2. Run optimization on normal data
    results_normal = optimizer.optimize(normal_data.copy())
    
    # 3. Create a profile with an EXTREME spike in the future (e.g., Hour 40)
    # Decisions before Hour 40 should not change, if no leakage exists.
    leakage_hour = 40
    data_with_leakage = normal_data.copy()
    data_with_leakage.loc[leakage_hour, 'DA_Price'] = 99999.0 # Extreme Spike
    
    # 4. Run optimization on leakage data
    results_leakage = optimizer.optimize(data_with_leakage.copy())
    
    # 5. ASSERATION: Compare results up to the hour BEFORE the leakage.
    # The decision at Hour 39 might change (to prepare SOC),
    # but decisions from Hour 0 to 38 MUST be identical.
    safe_zone_slice = slice(0, leakage_hour - 1) # Hours 0 to 38
    
    # Check that Discharge MW did not change based on future knowledge
    pd.testing.assert_series_equal(
        results_normal.loc[safe_zone_slice, 'Optimized_Discharge_MW'],
        results_leakage.loc[safe_zone_slice, 'Optimized_Discharge_MW'],
        obj=f"Discharge MW leakage detected before hour {leakage_hour}"
    )
    
    # Check that Charge MW did not change based on future knowledge
    pd.testing.assert_series_equal(
        results_normal.loc[safe_zone_slice, 'Optimized_Charge_MW'],
        results_leakage.loc[safe_zone_slice, 'Optimized_Charge_MW'],
        obj=f"Charge MW leakage detected before hour {leakage_hour}"
    )

    # Check that aFRR Reserve allocation did not change
    pd.testing.assert_series_equal(
        results_normal.loc[safe_zone_slice, 'Optimized_Reserve_MW'],
        results_leakage.loc[safe_zone_slice, 'Optimized_Reserve_MW'],
        obj=f"Reserve MW leakage detected before hour {leakage_hour}"
    )
