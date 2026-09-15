import pulp
import pandas as pd

class BESS_CoOptimizer:
    """
    Mixed-Integer Linear Programming (MILP) model for BESS Co-optimization.
    Handles Day-Ahead Arbitrage and aFRR Capacity Allocation.
    """
    def __init__(self, capacity_mwh: float, max_power_mw: float, efficiency: float = 0.9):
        self.capacity_mwh = capacity_mwh
        self.max_power_mw = max_power_mw
        self.efficiency = efficiency

    def optimize(self, df: pd.DataFrame) -> pd.DataFrame:
        model = pulp.LpProblem("BESS_CoOptimization", pulp.LpMaximize)
        time_steps = df.index.tolist()

        # Decision Variables
        p_charge = pulp.LpVariable.dicts("Charge_MW", time_steps, lowBound=0, upBound=self.max_power_mw)
        p_discharge = pulp.LpVariable.dicts("Discharge_MW", time_steps, lowBound=0, upBound=self.max_power_mw)
        cap_reserve = pulp.LpVariable.dicts("Reserve_MW", time_steps, lowBound=0, upBound=self.max_power_mw)
        soc = pulp.LpVariable.dicts("SoC_MWh", time_steps, lowBound=0, upBound=self.capacity_mwh)

        # Objective Function: Maximize Profit
        model += pulp.lpSum([
            p_discharge[t] * df.loc[t, 'DA_Price'] 
            - p_charge[t] * df.loc[t, 'DA_Price'] 
            + cap_reserve[t] * df.loc[t, 'Capacity_Price']
            for t in time_steps
        ]), "Total_Profit"

        # Constraints
        for t in time_steps:
            model += p_discharge[t] + cap_reserve[t] <= self.max_power_mw
            model += p_charge[t] <= self.max_power_mw
            
            # SoC Tracking
            if t == time_steps[0]:
                model += soc[t] == (self.capacity_mwh * 0.5) + (p_charge[t] * self.efficiency) - (p_discharge[t] / self.efficiency)
            else:
                model += soc[t] == soc[t-1] + (p_charge[t] * self.efficiency) - (p_discharge[t] / self.efficiency)
            
            # Energy availability for reserve activation
            model += soc[t] >= (cap_reserve[t] / self.efficiency)

        # Solve
        model.solve(pulp.PULP_CBC_CMD(msg=0))

        # Store Results
        df = df.copy()
        df['Optimized_Charge_MW'] = [p_charge[t].varValue for t in time_steps]
        df['Optimized_Discharge_MW'] = [p_discharge[t].varValue for t in time_steps]
        df['Optimized_Reserve_MW'] = [cap_reserve[t].varValue for t in time_steps]
        df['Optimized_SoC_MWh'] = [soc[t].varValue for t in time_steps]
        
        return df
