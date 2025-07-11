# Metrics Dashboard

This dashboard visualises recent model performance and the predicted best LLM.

## Setup

Install dependencies and run the dashboard:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The application reads from `inanna_ai/db_storage.py` and updates automatically
when new benchmarks are logged.
