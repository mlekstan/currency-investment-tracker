from pydantic import BaseModel, Field, RootModel


class CurrencyRate(BaseModel): 
    model_config = {"extra": "ignore"}
    code: str
    mid: float

class DailyInfo(BaseModel): 
    table: str
    no: str
    effective_date: str = Field(alias="effectiveDate")
    rates: list[CurrencyRate]

class NbpResponse(RootModel): 
    root: list[DailyInfo]