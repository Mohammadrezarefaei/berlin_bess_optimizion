import pandas as pd

class BalancingMarketSettlement:
    """
    Calculates financial settlement for balancing market participation,
    including capacity payments, energy activation, and imbalance penalties.
    """
    def __init__(self, capacity_mwh: float, max_power_mw: float, penalty_rate: float = 1.2):
        self.capacity = capacity_mwh
        self.max_power = max_power_mw
        self.penalty_rate = penalty_rate

    def calculate_settlement(self, scheduled_mw: float, actual_activated_mw: float, clearing_price: float, capacity_price: float = 0.0, reserved_mw: float = 0.0) -> dict:
        capacity_revenue = reserved_mw * capacity_price
        energy_revenue = actual_activated_mw * clearing_price
        
        deviation = abs(scheduled_mw - actual_activated_mw)
        imbalance_penalty = deviation * clearing_price * self.penalty_rate
        
        net_revenue = capacity_revenue + energy_revenue - imbalance_penalty
        
        return {
            "Capacity_Revenue": capacity_revenue,
            "Energy_Revenue": energy_revenue,
            "Imbalance_Penalty": imbalance_penalty,
            "Net_Settlement": net_revenue
        }
