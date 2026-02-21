# IPL Analytics Dashboard

Starter dashboard for IPL batting analytics using Kaggle ball-by-ball data (default: `ipl_data_full.csv`).

## What it shows
- Focused view for 2023 to 2025
- Tab 1 (`Runs & Wickets`):
  - Top 20 run scorers
  - Top 20 wicket takers
  - Combined view (2023-2025) and single-season view
- Tab 2 (`Phase-wise Runs`):
  - Top 20 run scorers in Overs 1-6, Overs 7-14, Overs 15-20
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 3 (`Phase-wise Wickets`):
  - Top 20 wicket takers in Overs 1-6, Overs 7-14, Overs 15-20
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 4 (`Batter Impact by Phase`):
  - Top 20 batters by strike rate in Overs 1-6, Overs 7-14, Overs 15-20
  - Strike Rate = (Runs scored / Balls faced) * 100
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 5 (`Bowling Impact by Phase`):
  - Top 20 bowlers by bowling strike rate in Overs 1-6, Overs 7-14, Overs 15-20
  - Bowling strike rate = Wickets taken / Balls bowled
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025

## Run locally
```bash
cd "/Users/vibhagopal/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

By default, the app reads:
`/Users/vibhagopal/Downloads/ipl_data_full.csv`

You can change the CSV path from the sidebar.
