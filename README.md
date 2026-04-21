# Sri Lanka CO2 Dashboard

Streamlit dashboard for exploring Sri Lanka CO2 equivalent emissions data for 2024 and 2025.

## Files

- `app.py`: Streamlit dashboard
- `clean_data.csv`: cleaned dataset used by the dashboard
- `clean_data.py`: data cleaning script
- `lka_co2e_20yr_source.csv`: original source dataset
- `requirements.txt`: Python dependencies for deployment

## Run locally

```powershell
python -m streamlit run app.py
```

## Rebuild the cleaned dataset

```powershell
python clean_data.py
```

If `clean_data.py` cannot save `clean_data.csv`, close the CSV in Excel or any other app and run it again.

## Deployment

This repository is ready to deploy on Streamlit Community Cloud with:

- Repository: `Sanuji2003/sri-lanka-co2-dashboard`
- Branch: `main`
- Entrypoint: `app.py`
