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
  - Minimum balls per phase: 60 for yearly views, 180 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 6 (`Batter Innings Summary`):
  - Top 20 batters by average balls batted per innings
  - Includes average runs per innings
  - Sorted by average balls per innings (descending)
  - Minimum 100 balls faced in selected scope (year-wise or combined)
- Tab 7 (`Dot Ball % by Phase`):
  - Top 20 bowlers by dot ball percentage in Overs 1-6, Overs 7-14, Overs 15-20
  - Dot Ball % = Dot balls / Balls bowled
  - Minimum balls per phase: 60 for yearly views, 180 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 8 (`Boundary Impact by Phase`):
  - Top 20 batters by boundaries hit / balls faced in Overs 1-6, Overs 7-14, Overs 15-20
  - Boundary = 4 or 6
  - Minimum balls per phase: 60 for yearly views, 180 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 9 (`Runs/Wicket by Phase`):
  - Top 20 bowlers by (Runs conceded / Wickets taken), ranked ascending
  - Minimum balls per phase: 60 for yearly views, 180 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 10 (`Batting Variance`):
  - Top 20 batters by least-to-most variance of runs per innings
  - Minimum runs scored: >250 for yearly views, >600 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 11 (`30+ Scores`):
  - Top 20 batters sorted by `% of 30+ Scores` (descending)
  - `% of 30+ Scores = (30+ Innings / Total Innings) * 100`
  - Minimum runs scored: >=250 for yearly views, >=600 for consolidated view
  - Separate tables for 2023, 2024, 2025, and combined 2023-2025
- Tab 12 (`2+ Wkts %`):
  - Top 20 bowlers sorted by `% of innings with 2+ wickets` (descending)
  - `% 2+ Wkt Innings = (2+ wicket innings / innings bowled) * 100`
  - Minimum matches played: >=7 for yearly views, >=18 for consolidated view
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
