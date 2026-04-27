from abc import ABC, abstractmethod

class Asset(ABC): 
    def __init__(self, code: str, capital: float) -> None:
        self.code = code
        self.capital = capital 
    
    @abstractmethod
    def get_daily_value(self, daily_stats: dict[str, dict]) -> float:
        pass


class CurrencyAsset(Asset): 
    def __init__(self, code: str, capital: float, purchase_rate: float) -> None:
        super().__init__(code, capital)
        self.foreign = capital / purchase_rate

    def get_daily_value(self, daily_stats: dict[str, dict]) -> float: 
        info = daily_stats.get(self.code, {})
        current_rate: float = info.get("rate", 0.0)

        return self.foreign * current_rate