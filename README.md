# Energy Poverty & Health Outcomes Analyzer

Analyzes how electricity access correlates with child mortality, 
life expectancy, and maternal mortality across 100+ countries (2000–2023).

## Live Demo
[Launch Dashboard](https://huggingface.co/spaces/malyan2313/energy-health)

## Tech Stack
- Python, Pandas, NumPy
- World Bank API (wbgapi)
- Two-way Fixed Effects Panel Regression (linearmodels)
- Plotly Express — choropleth maps & animated scatter
- Streamlit — interactive dashboard
- Deployed on Hugging Face Spaces

## Key Findings
- A 10pp increase in electricity access correlates with measurable 
  reduction in child mortality after controlling for GDP and urbanisation
- Panel regression controls for country fixed effects and global time trends
- Data: World Bank Development Indicators (2000–2023)

## Run Locally
pip install -r requirements.txt
streamlit run app.py
