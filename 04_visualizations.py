import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv("data/clean_panel.csv")

# --- Map 1: Electricity access in latest year ---
latest = df[df["year"] == df["year"].max()].copy()

fig_map = px.choropleth(
    latest,
    locations="country_code",
    color="electricity_access_pct",
    hover_name="country_name",
    hover_data={
        "electricity_access_pct": ":.1f",
        "child_mortality_per1000": ":.1f",
        "life_expectancy": ":.1f",
        "income_group": True,
    },
    color_continuous_scale="Blues",
    range_color=[0, 100],
    title=f"Electricity access by country ({df['year'].max()})",
    labels={"electricity_access_pct": "Access (%)"},
)
fig_map.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    coloraxis_colorbar=dict(title="Access %", thickness=15, len=0.5),
    margin=dict(l=0, r=0, t=50, b=0),
    height=500,
)
fig_map.write_html("outputs/map_electricity_access.html")

# --- Map 2: Child mortality ---
fig_map2 = px.choropleth(
    latest,
    locations="country_code",
    color="child_mortality_per1000",
    hover_name="country_name",
    color_continuous_scale="Reds",
    title=f"Under-5 child mortality per 1,000 ({df['year'].max()})",
    labels={"child_mortality_per1000": "Deaths/1000"},
)
fig_map2.update_layout(
    geo=dict(showframe=False, projection_type="natural earth"),
    height=500,
)
fig_map2.write_html("outputs/map_child_mortality.html")

# --- Scatter: electricity access vs child mortality, animated by year ---
fig_scatter = px.scatter(
    df,
    x="electricity_access_pct",
    y="child_mortality_per1000",
    animation_frame="year",
    animation_group="country_code",
    size="gdp_per_capita_ppp",
    color="income_group",
    hover_name="country_name",
    log_y=True,
    range_x=[0, 101],
    labels={
        "electricity_access_pct": "Electricity access (%)",
        "child_mortality_per1000": "Child mortality (per 1,000, log scale)",
        "income_group": "Income group",
    },
    title="Electricity access vs child mortality (2000–2022)",
    color_discrete_map={
        "High income": "#185FA5",
        "Upper-middle income": "#1D9E75",
        "Lower-middle income": "#EF9F27",
        "Low income": "#E24B4A",
    },
)
fig_scatter.update_layout(height=550)
fig_scatter.write_html("outputs/scatter_animated.html")

print("All charts saved to outputs/")