from datetime import date, timedelta

import streamlit as st

from api.api_client import HttpApiClientConfig
from api.nbp_service import HttpApiClient, NbpService
from core import asset
from core.investment import Investment, InvestmentSimulator


def main():
    st.set_page_config(layout="wide")
    st.title("Currency Investment Tracker")

    min_date = date.fromisoformat("2002-01-02")
    max_date = date.today() - timedelta(1)

    http_client_config = HttpApiClientConfig("https", "api.nbp.pl")
    http_api_client = HttpApiClient(http_client_config)
    nbp_service = NbpService(http_api_client, "%Y-%m-%d")

    with st.container(border=True):
        st.subheader("Define investment params")

        capital = st.number_input(
            label="Initial capital [PLN]",
            min_value=0.0,
            value=1000.0,
            step=0.01, 
            format="%.2f", 
            width=200
        )

        start_date = st.date_input(
            label="Start date", 
            value=date.today() - timedelta(1), 
            min_value=min_date, 
            max_value=max_date, 
            width=200
        )

        days = st.selectbox(
            label="Days range", 
            options=[i for i in range(1, 31) if i <= (date.today() - start_date).days], 
            width=200
        )

        end_date = start_date + timedelta(days)


        # Fetching data
        exchange_rates = nbp_service.get_full_exchange_rates(start_date, end_date)
        all_currencies_codes = nbp_service.extract_currency_codes(exchange_rates)


        col1, col2, col3 = st.columns(3)
        with col1:
            c1 = st.selectbox("Select currency 1", all_currencies_codes, key="c1", index=0)
            p1 = st.slider("Share %", 0, 100, 33, key="s1")

        with col2:
            options_c2 = [c for c in all_currencies_codes if c != c1]
            c2 = st.selectbox("Select currency 2", options_c2, key="c2", index=0)
            p2 = st.slider("Share %", 0, 100, 33, key="s2")

        with col3:
            options_c3 = [w for w in all_currencies_codes if w not in [c1, c2]]
            c3 = st.selectbox("Select currency 3", options_c3, key="c3", index=0)
            p3 = st.slider("Share %", 0, 100, 34, key="s3")

        total_p = p1 + p2 + p3
        if total_p != 100:
            st.warning(f"Total of shares is {total_p}%. It should be 100%.")
            st.stop()


        # Transforming fetched data to frindly format
        history = nbp_service.transform_to_history(exchange_rates)          
        
        first_date = sorted(history.keys())[0]
        day_one_prices = history[first_date]

        cp1 = round((p1 / 100.0) * capital, 2)
        cp2 = round((p2 / 100.0) * capital, 2)
        cp3 = round(capital - cp1 - cp2, 2)  

        try:
            asset1 = asset.CurrencyAsset(c1, cp1, day_one_prices[c1]["rate"])
            asset2 = asset.CurrencyAsset(c2, cp2, day_one_prices[c2]["rate"])
            asset3 = asset.CurrencyAsset(c3, cp3, day_one_prices[c3]["rate"])

            investment = Investment(capital, assets=[asset1, asset2, asset3])
            
        except ValueError as e:
            st.error(f"Investment initialization error: {e}")
            st.stop()

        simulator = InvestmentSimulator(investment, history)
        df_result = simulator.simulate()
        df_result = df_result.set_index("Date")



    with st.container(border=True):
        st.subheader("Change of shares in investment (start vs. end)")
        
        first_day = df_result.iloc[0]
        last_day = df_result.iloc[-1]
        share_columns = [col for col in df_result.columns if col not in ["Investment value", "Difference"]]
        metric_cols = st.columns(len(share_columns))

        for i, currency in enumerate(share_columns):
            start_share = first_day[currency]
            end_share = last_day[currency]
            
            diff_share = end_share - start_share

            with metric_cols[i]:
                st.metric(
                    label=f"Share {currency}",
                    value=f"{end_share:.2f} %",
                    delta=f"{diff_share:.2f} p.p."
                )


    with st.container(border=True): 
        st.subheader("Investment value over the time [PLN]")
        st.line_chart(df_result["Investment value"])

    with st.container(border=True):
        st.subheader("Daily difference [PLN]")
        st.bar_chart(df_result["Difference"])


if __name__ == "__main__":
    main()