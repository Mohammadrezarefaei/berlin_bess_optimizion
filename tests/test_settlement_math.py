import pytest
from src.settlement import BalancingMarketSettlement

@pytest.fixture
def settlement_engine():
    """Returns a settlement engine with 10MWh, 5MW, 1.2 penalty rate."""
    return BalancingMarketSettlement(capacity_mwh=10.0, max_power_mw=5.0, penalty_rate=1.2)

def test_settlement_full_activation_no_deviation(settlement_engine):
    """
    Test scenario: Battery reservations 5MW, full 5MW activation requested, 
    BESS delivers full 5MW. (Zero Deviation)
    """
    clearing_price = 100.0 # €/MWh
    capacity_price = 20.0  # €/MW
    reserved_mw = 5.0
    
    results = settlement_engine.calculate_settlement(
        scheduled_mw=reserved_mw, 
        actual_activated_mw=reserved_mw, 
        clearing_price=clearing_price,
        capacity_price=capacity_price,
        reserved_mw=reserved_mw
    )
    
    # Calculation:
    # Cap Rev: 5 * 20 = 100
    # Energy Rev: 5 * 100 = 500
    # Penalty: 0 * ... = 0
    # Net: 100 + 500 - 0 = 600
    
    assert results['Net_Settlement'] == 600.0
    assert results['Imbalance_Penalty'] == 0.0

def test_settlement_imbalance_penalty(settlement_engine):
    """
    Test scenario: Battery reservations 5MW. Requested to activate 5MW, 
    but only delivers 3MW due to SoC constraint. (2MW Deviation)
    """
    clearing_price = 100.0 # €/MWh
    capacity_price = 20.0  # €/MW (earned regardless of activation)
    reserved_mw = 5.0
    actual_activated = 3.0 # The failure
    
    results = settlement_engine.calculate_settlement(
        scheduled_mw=reserved_mw, 
        actual_activated_mw=actual_activated, 
        clearing_price=clearing_price,
        capacity_price=capacity_price,
        reserved_mw=reserved_mw
    )
    
    # Calculation:
    # Cap Rev: 5 * 20 = 100 (Still earned if reservation was reliable)
    # Energy Rev: 3 * 100 = 300
    # Deviation: abs(5 - 3) = 2 MWh
    # Penalty: 2 * 100 * 1.2 (penalty rate) = 240
    # Net: 100 + 300 - 240 = 160
    
    assert results['Capacity_Revenue'] == 100.0
    assert results['Energy_Revenue'] == 300.0
    assert results['Imbalance_Penalty'] == 240.0
    assert results['Net_Settlement'] == 160.0
