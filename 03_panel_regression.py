import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

df = pd.read_csv("data/clean_panel.csv")

# Set panel index: (entity, time)
df = df.set_index(["country_code", "year"])

# Model 1: Electricity access → child mortality (two-way FE)
# log_child_mort = β₁·electricity_access + β₂·log_gdp + β₃·urban + αᵢ + γₜ + ε
y = df["log_child_mortality"]
X = df[["electricity_access_pct", "log_gdp_pc", "urban_population_pct"]]
X = sm.add_constant(X)

model_child = PanelOLS(
    dependent=y,
    exog=X,
    entity_effects=True,   # Country fixed effects (removes time-invariant confounders)
    time_effects=True       # Year fixed effects (removes global shocks)
)
result_child = model_child.fit(cov_type="clustered", cluster_entity=True)
print("=== Model 1: Child Mortality ===")
print(result_child.summary)

# Model 2: Electricity access → life expectancy
y2 = df["life_expectancy"]
model_life = PanelOLS(dependent=y2, exog=X,
                      entity_effects=True, time_effects=True)
result_life = model_life.fit(cov_type="clustered", cluster_entity=True)
print("\n=== Model 2: Life Expectancy ===")
print(result_life.summary)

# Model 3: Electricity access → maternal mortality
df_mat = df.dropna(subset=["log_maternal_mortality"])
y3 = df_mat["log_maternal_mortality"]
X3 = df_mat[["electricity_access_pct", "log_gdp_pc", "urban_population_pct"]]
X3 = sm.add_constant(X3)
model_mat = PanelOLS(dependent=y3, exog=X3,
                     entity_effects=True, time_effects=True)
result_mat = model_mat.fit(cov_type="clustered", cluster_entity=True)
print("\n=== Model 3: Maternal Mortality ===")
print(result_mat.summary)

# Save coefficients for the dashboard
results_summary = {
    "model": ["Child mortality", "Life expectancy", "Maternal mortality"],
    "coef": [
        result_child.params["electricity_access_pct"],
        result_life.params["electricity_access_pct"],
        result_mat.params["electricity_access_pct"],
    ],
    "pval": [
        result_child.pvalues["electricity_access_pct"],
        result_life.pvalues["electricity_access_pct"],
        result_mat.pvalues["electricity_access_pct"],
    ],
    "ci_low": [
        result_child.conf_int().loc["electricity_access_pct", "lower"],
        result_life.conf_int().loc["electricity_access_pct", "lower"],
        result_mat.conf_int().loc["electricity_access_pct", "lower"],
    ],
    "ci_high": [
        result_child.conf_int().loc["electricity_access_pct", "upper"],
        result_life.conf_int().loc["electricity_access_pct", "upper"],
        result_mat.conf_int().loc["electricity_access_pct", "upper"],
    ],
}
pd.DataFrame(results_summary).to_csv("data/regression_results.csv", index=False)