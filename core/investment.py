from datetime import date

import pandas as pd

from core.asset import Asset


class Investment: 
    def __init__(self, initial_capital: float, assets: list[Asset]) -> None:
        self.initial_capital = initial_capital
        self.assets = assets
        
        if not assets:
            raise ValueError("Investment must have assets.")

        total_allocated = sum(asset.capital for asset in self.assets)
        
        if round(total_allocated, 2) != round(initial_capital, 2):
            raise ValueError(
                f"Sum of allocated capital ({total_allocated:.2f}) "
                f"must be equal to initial capital ({initial_capital:.2f})."
            )
        
    
    def get_daily_value(self, daily_stats: dict[str, dict]): 
        investment_value = 0
        for asset in self.assets:
            asset_value = asset.get_daily_value(daily_stats)
            investment_value += asset_value
        
        return investment_value


class InvestmentSimulator:
    def __init__(self, investment: Investment, history: dict[date, dict]): 
        self.investment = investment
        self.history = history
	
    def simulate(self): 
        result = []
        prev_investment_value = self.investment.initial_capital

        for curr_date, daily_stats in sorted(self.history.items()): 

            investment_value = self.investment.get_daily_value(daily_stats)

            row = {
                "Date": curr_date, 
                "Investment value": investment_value, 
            }

            sum_share = 0
            for i, asset in enumerate(self.investment.assets): 
                asset_value = asset.get_daily_value(daily_stats)
                share = 0.0
                if investment_value > 0: 
                    if i == len(self.investment.assets) - 1:
                        share = round(100.0 - sum_share, 2)
                    else: 
                        share = round((asset_value / investment_value) * 100, 2)
                
                row[asset.code] = share
                sum_share += share
                
            diff = investment_value - prev_investment_value
            row["Difference"] = diff
            prev_investment_value = investment_value
            
            result.append(row)
           
        return pd.DataFrame(result).round(2)