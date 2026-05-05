import pandas as pd
import numpy as np
import wbgapi as wb

df = pd.read_csv("data/raw_panel.csv")

print("Columns:", df.columns.tolist())
print("Shape:", df.shape)

# Drop rows missing key variables
df.dropna(subset=["electricity_access_pct", "child_mortality_per1000",
                   "life_expectancy", "gdp_per_capita_ppp"], inplace=True)

# Log-transform skewed variables
df["log_gdp_pc"] = np.log(df["gdp_per_capita_ppp"])
df["log_child_mortality"] = np.log(df["child_mortality_per1000"] + 1)
df["log_maternal_mortality"] = np.log(df["maternal_mortality_per100k"] + 1)

# Fetch income group metadata from World Bank
meta = wb.economy.DataFrame()[["incomeLevel"]].reset_index()
meta.rename(columns={"id": "country_code", "incomeLevel": "income_group"}, inplace=True)

# Print actual codes returned by wbgapi so we can verify
print("Unique income codes:", meta["income_group"].unique())

income_map = {
    "HIC": "High income",
    "UMC": "Upper-middle income",
    "LMC": "Lower-middle income",
    "LIC": "Low income",
    "INX": "Not classified",
}
meta["income_group"] = meta["income_group"].map(income_map).fillna("Unknown")

df = df.merge(meta, on="country_code", how="left")

# Keep only countries with at least 10 years of data
country_counts = df.groupby("country_code")["year"].count()
valid_countries = country_counts[country_counts >= 10].index
df = df[df["country_code"].isin(valid_countries)]

print(f"Final panel: {df['country_code'].nunique()} countries × {df['year'].nunique()} years")
print("Income group distribution:")
print(df["income_group"].value_counts())

df.to_csv("data/clean_panel.csv", index=False)
print("Saved to data/clean_panel.csv")