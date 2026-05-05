import pandas as pd
import numpy as np

df = pd.read_csv("data/raw_panel.csv")

# Drop rows missing key variables
df.dropna(subset=["electricity_access_pct", "child_mortality_per1000",
                   "life_expectancy", "gdp_per_capita_ppp"], inplace=True)

# Log-transform skewed variables — standard in economics panel work
df["log_gdp_pc"] = np.log(df["gdp_per_capita_ppp"])
df["log_child_mortality"] = np.log(df["child_mortality_per1000"] + 1)
df["log_maternal_mortality"] = np.log(df["maternal_mortality_per100k"] + 1)

# Add income group labels via World Bank classification
income_map = {
    "H": "High income",
    "UM": "Upper-middle income",
    "LM": "Lower-middle income",
    "L": "Low income"
}

import wbgapi as wb
meta = wb.economy.DataFrame()[["incomeLevel"]].reset_index()
meta.rename(columns={"id": "country_code", "incomeLevel": "income_group"}, inplace=True)
meta["income_group"] = meta["income_group"].map(income_map).fillna("Unknown")

df = df.merge(meta, on="country_code", how="left")

# Keep only countries with at least 10 years of data (balanced-ish panel)
country_counts = df.groupby("country_code")["year"].count()
valid_countries = country_counts[country_counts >= 10].index
df = df[df["country_code"].isin(valid_countries)]

df.to_csv("data/clean_panel.csv", index=False)
print(f"Final panel: {df['country_code'].nunique()} countries × {df['year'].nunique()} years")
print(df.describe())