from datetime import date, timedelta

from api.api_client import HttpApiClient, HttpException
from api.dto import DailyInfo, NbpResponse


class NbpService: 
    def __init__(self, api_client: HttpApiClient, date_format: str): 
        self.api_client = api_client
        self.date_format = date_format
    

    def get_exchange_rates(self, start_date: date, end_date: date): 
        start_date_str = start_date.strftime(self.date_format)
        end_date_str = end_date.strftime(self.date_format)

        response = self.api_client.make_request(f"api/exchangerates/tables/A/{start_date_str}/{end_date_str}", {
            "method": "GET", 
            "headers": {
                "Accept": "application/json"
            }
        }) 

        raw_data = response.json()
        data = NbpResponse.model_validate(raw_data).root

        return data


    def get_full_exchange_rates(self, start_date: date, end_date: date): 
        real_start_date = start_date
        real_end_date = end_date
        
        start_date_weekday = start_date.weekday()
        if start_date_weekday == 5:
            start_date -= timedelta(1) 
        elif start_date_weekday == 6: 
            start_date -= timedelta(2)
            
        start_date_str = start_date.strftime(self.date_format)
        
        data = []
        need_more_data = False
        try: 
            data = self.get_exchange_rates(start_date, end_date)
            
            if not data or data[0].effective_date != start_date_str:
                need_more_data = True
                
        except HttpException as e:
            if e.code == 404:
                need_more_data = True

        if need_more_data: 
            more_data = [] 
            
            search_start = start_date - timedelta(6)
            search_end = start_date - timedelta(1)
                       
            while len(more_data) == 0:
                try: 
                    more_data = self.get_exchange_rates(search_start, search_end)
                except HttpException as e:
                    if e.code == 404:
                        search_start -= timedelta(6)
                        search_end -= timedelta(6)
                        continue
            
            data.insert(0, more_data[-1])

        full_data: list[DailyInfo] = []

        for i in range(len(data)):
            daily_info = data[i]

            if i + 1 < len(data):
                comparison_date = date.fromisoformat(data[i+1].effective_date)
            else:
                comparison_date = real_end_date + timedelta(1)

            while comparison_date > real_start_date:
                
                daily_info_copy = daily_info.model_copy()
                daily_info_copy.effective_date = real_start_date.strftime(self.date_format)
                
                full_data.append(daily_info_copy)
                real_start_date += timedelta(1)

        return full_data

    
    def transform_to_history(self, full_exchange_rates: list[DailyInfo]): 
        history: dict[date, dict] = {}
        for daily_info in full_exchange_rates:
            daily_stats = {}

            for currency_info in daily_info.rates: 
                daily_stats[currency_info.code] = {
                    "rate": currency_info.mid
                }

            curr_date = date.fromisoformat(daily_info.effective_date)
            history[curr_date] = daily_stats

        return history


    def extract_currency_codes(self, full_exchange_rates: list[DailyInfo]):
        rates = full_exchange_rates[0].rates
        codes = [rate.code for rate in rates]

        return sorted(codes)