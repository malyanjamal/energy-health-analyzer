# app.py  — run with: streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Energy poverty & health outcomes",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("data/clean_panel.csv")
    reg = pd.read_csv("data/regression_results.csv")
    return df, reg

df, reg = load_data()

st.title("Energy poverty & global health outcomes")
st.markdown(
    "Analyzing how electricity access correlates with child mortality, "
    "life expectancy, and maternal mortality across 100+ countries (2000–2022)."
)

# --- Sidebar filters ---
st.sidebar.header("Filters")
year = st.sidebar.slider(
    "Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max())
)
income_groups = st.sidebar.multiselect(
    "Income groups",
    options=df["income_group"].dropna().unique().tolist(),
    default=df["income_group"].dropna().unique().tolist()
)
metric = st.sidebar.selectbox(
    "Health metric",
    options=["child_mortality_per1000", "life_expectancy", "maternal_mortality_per100k"],
    format_func=lambda x: {
        "child_mortality_per1000": "Child mortality (per 1,000)",
        "life_expectancy": "Life expectancy (years)",
        "maternal_mortality_per100k": "Maternal mortality (per 100k)"
    }[x]
)

filtered = df[(df["year"] == year) & (df["income_group"].isin(income_groups))]

# --- KPI row ---
col1, col2, col3 = st.columns(3)
col1.metric("Countries in view", len(filtered))
col2.metric(
    "Avg electricity access",
    f"{filtered['electricity_access_pct'].mean():.1f}%"
)
col3.metric(
    "Avg child mortality",
    f"{filtered['child_mortality_per1000'].mean():.1f}"
)

st.divider()

# --- Choropleth ---
st.subheader(f"Global electricity access — {year}")
fig_map = px.choropleth(
    filtered,
    locations="country_code",
    color="electricity_access_pct",
    hover_name="country_name",
    hover_data={"electricity_access_pct": ":.1f", metric: ":.1f"},
    color_continuous_scale="Blues",
    range_color=[0, 100],
)
fig_map.update_layout(
    geo=dict(showframe=False, projection_type="natural earth"),
    height=420,
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Access %", thickness=12, len=0.4)
)
st.plotly_chart(fig_map, use_container_width=True)

# --- Scatter ---
st.subheader(f"Electricity access vs {metric.replace('_', ' ')} — {year}")
fig_scatter = px.scatter(
    filtered,
    x="electricity_access_pct",
    y=metric,
    color="income_group",
    size="gdp_per_capita_ppp",
    hover_name="country_name",
    trendline="ols",
    labels={"electricity_access_pct": "Electricity access (%)"},
    color_discrete_map={
        "High income": "#185FA5",
        "Upper-middle income": "#1D9E75",
        "Lower-middle income": "#EF9F27",
        "Low income": "#E24B4A",
    }
)
fig_scatter.update_layout(height=420)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Regression results ---
st.subheader("Panel regression results (two-way fixed effects)")
st.markdown(
    "Each coefficient shows the effect of a **1 percentage point increase in electricity access**, "
    "controlling for GDP per capita, urbanisation, country fixed effects, and year fixed effects."
)

for _, row in reg.iterrows():
    sig = "✓ Significant" if row["pval"] < 0.05 else "Not significant"
    color = "green" if row["pval"] < 0.05 else "gray"
    st.markdown(
        f"**{row['model']}** — coefficient: `{row['coef']:.4f}` "
        f"(95% CI: {row['ci_low']:.4f} to {row['ci_high']:.4f}) "
        f"p = {row['pval']:.3f} — :{color}[{sig}]"
    )

# --- Time series for selected country ---
st.divider()
st.subheader("Country deep-dive")
country = st.selectbox(
    "Select a country",
    options=sorted(df["country_name"].dropna().unique()),
    index=list(sorted(df["country_name"].dropna().unique())).index("Pakistan")
    if "Pakistan" in df["country_name"].values else 0
)
cdf = df[df["country_name"] == country].sort_values("year")

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=cdf["year"], y=cdf["electricity_access_pct"],
    name="Electricity access (%)", yaxis="y1", line=dict(color="#185FA5")
))
fig_ts.add_trace(go.Scatter(
    x=cdf["year"], y=cdf["child_mortality_per1000"],
    name="Child mortality/1000", yaxis="y2", line=dict(color="#E24B4A", dash="dash")
))
fig_ts.update_layout(
    yaxis=dict(title="Electricity access (%)", color="#185FA5"),
    yaxis2=dict(title="Child mortality", overlaying="y", side="right", color="#E24B4A"),
    legend=dict(orientation="h", y=1.1),
    height=380,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(title="Year")
)
st.plotly_chart(fig_ts, use_container_width=True)

st.caption(
    "Data: World Bank Development Indicators. "
    "Methodology: Two-way fixed effects panel OLS with country-clustered standard errors."
)