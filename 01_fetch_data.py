# requirements:
# pip install wbgapi pandas plotly statsmodels linearmodels openpyxl

import wbgapi as wb
import pandas as pd

INDICATORS = {
    "EG.ELC.ACCS.ZS":   "electricity_access_pct",   # World Bank
    "SH.DYN.MORT":       "child_mortality_per1000",  # World Bank (under-5)
    "SP.DYN.LE00.IN":    "life_expectancy",           # World Bank
    "SH.STA.MMRT":       "maternal_mortality_per100k",# World Bank
    "NY.GDP.PCAP.PP.KD": "gdp_per_capita_ppp",        # World Bank (control variable)
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",      # World Bank (control variable)
}

YEARS = range(2000, 2026)

def fetch_world_bank_data(indicators: dict, years) -> pd.DataFrame:
    frames = []
    for code, name in indicators.items():
        print(f"Fetching: {name} ({code})")
        df = wb.data.DataFrame(
            series=code,
            time=years,
            labels=True,
            numericTimeKeys=True
        ).reset_index()
        df = df.melt(
            id_vars=["economy", "Country"],
            var_name="year",
            value_name=name
        )
        df.rename(columns={"economy": "country_code", "Country": "country_name"}, inplace=True)
        df["year"] = df["year"].astype(int)
        frames.append(df.set_index(["country_code", "country_name", "year"]))

    combined = pd.concat(frames, axis=1).reset_index()
    return combined

raw_df = fetch_world_bank_data(INDICATORS, YEARS)
raw_df.to_csv("data/raw_panel.csv", index=False)
print(f"Shape: {raw_df.shape}")
print(raw_df.head())