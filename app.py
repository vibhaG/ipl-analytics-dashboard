from __future__ import annotations

import ast
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

import pandas as pd
import streamlit as st

st.set_page_config(page_title="IPL 2023-2025 Dashboards", layout="wide")

DEFAULT_DATA_PATH = BASE_DIR / "data" / "ipl_data_full.csv"
FOCUS_YEARS = [2023, 2024, 2025]
TOP_N = 20
PHASE_ORDER = ["Overs 1-6", "Overs 7-14", "Overs 15-20"]
BOWLER_WICKET_KINDS = {
    "bowled",
    "caught",
    "caught and bowled",
    "lbw",
    "stumped",
    "hit wicket",
}

HOME_VENUES_BY_FRANCHISE = {
    "Chennai Super Kings": {
        "MA Chidambaram Stadium",
    },
    "Mumbai Indians": {
        "Wankhede Stadium",
    },
    "Kolkata Knight Riders": {
        "Eden Gardens",
    },
    "Royal Challengers Bengaluru": {
        "M Chinnaswamy Stadium",
    },
    "Sunrisers Hyderabad": {
        "Rajiv Gandhi International Stadium",
    },
    "Gujarat Titans": {
        "Narendra Modi Stadium",
    },
    "Lucknow Super Giants": {
        "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium",
    },
    "Delhi Capitals": {
        "Arun Jaitley Stadium",
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
    },
    "Rajasthan Royals": {
        "Sawai Mansingh Stadium",
        "Barsapara Cricket Stadium",
    },
    "Punjab Kings": {
        "Maharaja Yadavindra Singh International Cricket Stadium",
        "Himachal Pradesh Cricket Association Stadium",
        "Punjab Cricket Association IS Bindra Stadium",
    },
}

PLAYER_DISPLAY_OVERRIDES = {
    "SS Iyer": "Shreyas Iyer",
    "JC Buttler": "Jos Buttler",
}
NEHAL_BATTER_NAME = "N Wadhera"
NEHAL_BATTER_LABEL = "Nehal Wadhera"
NAMAN_BATTER_NAME = "Naman Dhir"
NAMAN_BATTER_LABEL = "Naman Dhir"
ANGKRISH_BATTER_NAME = "A Raghuvanshi"
ANGKRISH_BATTER_LABEL = "Angkrish Raghuvanshi"
AYUSH_BATTER_NAME = "A Badoni"
AYUSH_BATTER_LABEL = "Ayush Badoni"
DEWALD_BATTER_NAME = "D Brevis"
DEWALD_BATTER_LABEL = "Dewald Brevis"


@st.cache_data(show_spinner=False)
def load_ipl_data(data_path: str) -> pd.DataFrame:
    df = pd.read_csv(data_path, low_memory=False)

    batter_candidates = ["striker", "batter"]
    non_striker_candidates = ["non_striker"]
    runs_candidates = ["runs_off_bat", "runs_batter"]
    bowler_candidates = ["bowler"]
    batting_team_candidates = ["batting_team"]
    bowling_team_candidates = ["bowling_team"]
    team_a_candidates = ["team_a"]
    team_b_candidates = ["team_b"]
    wicket_fielders_candidates = ["wicket_fielders"]
    replacement_in_candidates = ["replacement_in"]
    replacements_out_candidates = ["replacements_out", "replacement_out"]
    wicket_kind_candidates = ["wicket_kind", "wicket_type"]
    over_index_candidates = ["ball_over", "over"]
    wides_candidates = ["extra_wides", "wides"]
    noballs_candidates = ["extra_noballs", "noballs"]
    total_runs_candidates = ["runs_total", "total_runs"]
    extras_candidates = ["extras", "runs_extras"]
    match_id_candidates = ["match_id", "id"]
    innings_candidates = ["innings", "innings_val"]
    venue_candidates = ["venue"]
    city_candidates = ["city"]
    date_candidates = ["dates", "start_date", "date"]

    batter_col = next((col for col in batter_candidates if col in df.columns), None)
    non_striker_col = next((col for col in non_striker_candidates if col in df.columns), None)
    runs_col = next((col for col in runs_candidates if col in df.columns), None)
    bowler_col = next((col for col in bowler_candidates if col in df.columns), None)
    batting_team_col = next((col for col in batting_team_candidates if col in df.columns), None)
    bowling_team_col = next((col for col in bowling_team_candidates if col in df.columns), None)
    team_a_col = next((col for col in team_a_candidates if col in df.columns), None)
    team_b_col = next((col for col in team_b_candidates if col in df.columns), None)
    wicket_fielders_col = next((col for col in wicket_fielders_candidates if col in df.columns), None)
    replacement_in_col = next((col for col in replacement_in_candidates if col in df.columns), None)
    replacements_out_col = next((col for col in replacements_out_candidates if col in df.columns), None)
    wicket_kind_col = next((col for col in wicket_kind_candidates if col in df.columns), None)
    over_index_col = next((col for col in over_index_candidates if col in df.columns), None)
    wides_col = next((col for col in wides_candidates if col in df.columns), None)
    noballs_col = next((col for col in noballs_candidates if col in df.columns), None)
    total_runs_col = next((col for col in total_runs_candidates if col in df.columns), None)
    extras_col = next((col for col in extras_candidates if col in df.columns), None)
    match_id_col = next((col for col in match_id_candidates if col in df.columns), None)
    innings_col = next((col for col in innings_candidates if col in df.columns), None)
    venue_col = next((col for col in venue_candidates if col in df.columns), None)
    city_col = next((col for col in city_candidates if col in df.columns), None)
    date_col = next((col for col in date_candidates if col in df.columns), None)
    ball_col = "ball" if "ball" in df.columns else None

    if "season" not in df.columns or not batter_col or not runs_col or not bowler_col:
        raise ValueError(
            "Could not find required columns. Expected: season + batter + runs + bowler columns."
        )

    keep_cols = ["season", batter_col, runs_col, bowler_col]
    if non_striker_col:
        keep_cols.append(non_striker_col)
    if batting_team_col:
        keep_cols.append(batting_team_col)
    if bowling_team_col:
        keep_cols.append(bowling_team_col)
    if team_a_col:
        keep_cols.append(team_a_col)
    if team_b_col:
        keep_cols.append(team_b_col)
    if wicket_fielders_col:
        keep_cols.append(wicket_fielders_col)
    if replacement_in_col:
        keep_cols.append(replacement_in_col)
    if replacements_out_col:
        keep_cols.append(replacements_out_col)
    if wicket_kind_col:
        keep_cols.append(wicket_kind_col)
    if over_index_col:
        keep_cols.append(over_index_col)
    if wides_col:
        keep_cols.append(wides_col)
    if noballs_col:
        keep_cols.append(noballs_col)
    if total_runs_col:
        keep_cols.append(total_runs_col)
    if extras_col:
        keep_cols.append(extras_col)
    if match_id_col:
        keep_cols.append(match_id_col)
    if innings_col:
        keep_cols.append(innings_col)
    if venue_col:
        keep_cols.append(venue_col)
    if city_col:
        keep_cols.append(city_col)
    if date_col:
        keep_cols.append(date_col)
    if ball_col:
        keep_cols.append(ball_col)

    df = df[keep_cols].copy()

    rename_map = {
        batter_col: "batter",
        runs_col: "runs",
        bowler_col: "bowler",
    }
    if non_striker_col:
        rename_map[non_striker_col] = "non_striker"
    if batting_team_col:
        rename_map[batting_team_col] = "batting_team"
    if bowling_team_col:
        rename_map[bowling_team_col] = "bowling_team"
    if team_a_col:
        rename_map[team_a_col] = "team_a"
    if team_b_col:
        rename_map[team_b_col] = "team_b"
    if wicket_fielders_col:
        rename_map[wicket_fielders_col] = "wicket_fielders"
    if replacement_in_col:
        rename_map[replacement_in_col] = "replacement_in"
    if replacements_out_col:
        rename_map[replacements_out_col] = "replacements_out"
    if wicket_kind_col:
        rename_map[wicket_kind_col] = "wicket_kind"
    if over_index_col:
        rename_map[over_index_col] = "over_index"
    if wides_col:
        rename_map[wides_col] = "wides"
    if noballs_col:
        rename_map[noballs_col] = "noballs"
    if total_runs_col:
        rename_map[total_runs_col] = "total_runs"
    if extras_col:
        rename_map[extras_col] = "extras"
    if match_id_col:
        rename_map[match_id_col] = "match_id"
    if innings_col:
        rename_map[innings_col] = "innings_id"
    if venue_col:
        rename_map[venue_col] = "venue"
    if city_col:
        rename_map[city_col] = "city"
    if date_col:
        rename_map[date_col] = "match_date_raw"
    if ball_col:
        rename_map[ball_col] = "ball"
    df = df.rename(columns=rename_map)

    if "wicket_kind" not in df.columns:
        df["wicket_kind"] = ""

    # Some files encode season as strings like "{2018}".
    df["season"] = df["season"].astype(str).str.extract(r"(\d{4})", expand=False)
    df["season"] = pd.to_numeric(df["season"], errors="coerce")

    df["runs"] = pd.to_numeric(df["runs"], errors="coerce").fillna(0)
    df["wicket_kind"] = df["wicket_kind"].fillna("").astype(str).str.strip().str.lower()
    if "wides" in df.columns:
        df["wides"] = pd.to_numeric(df["wides"], errors="coerce").fillna(0)
    else:
        df["wides"] = 0
    if "noballs" in df.columns:
        df["noballs"] = pd.to_numeric(df["noballs"], errors="coerce").fillna(0)
    else:
        df["noballs"] = 0
    if "extras" in df.columns:
        df["extras"] = pd.to_numeric(df["extras"], errors="coerce").fillna(0)
    else:
        df["extras"] = pd.NA
    if "total_runs" in df.columns:
        df["total_runs"] = pd.to_numeric(df["total_runs"], errors="coerce")
    else:
        df["total_runs"] = pd.NA
    if "match_id" not in df.columns:
        df["match_id"] = pd.NA
    if "innings_id" not in df.columns:
        df["innings_id"] = pd.NA
    if "venue" not in df.columns:
        df["venue"] = "Unknown"
    if "city" not in df.columns:
        df["city"] = "Unknown"
    if "non_striker" not in df.columns:
        df["non_striker"] = pd.NA
    if "batting_team" not in df.columns:
        df["batting_team"] = pd.NA
    if "bowling_team" not in df.columns:
        df["bowling_team"] = pd.NA
    if "team_a" not in df.columns:
        df["team_a"] = pd.NA
    if "team_b" not in df.columns:
        df["team_b"] = pd.NA
    if "wicket_fielders" not in df.columns:
        df["wicket_fielders"] = pd.NA
    if "replacement_in" not in df.columns:
        df["replacement_in"] = pd.NA
    if "replacements_out" not in df.columns:
        df["replacements_out"] = pd.NA
    if "match_date_raw" not in df.columns:
        df["match_date_raw"] = pd.NA

    if "over_index" in df.columns:
        df["over_number"] = pd.to_numeric(df["over_index"], errors="coerce")
        valid_over = df["over_number"].dropna()
        if not valid_over.empty and valid_over.min() >= 0 and valid_over.max() <= 19:
            # Convert 0-based over index into cricket over numbers.
            df["over_number"] = df["over_number"] + 1
    elif "ball" in df.columns:
        ball_numeric = pd.to_numeric(df["ball"], errors="coerce")
        df["over_number"] = ball_numeric.floordiv(1) + 1
    else:
        df["over_number"] = pd.NA

    df = df.dropna(subset=["season", "batter", "bowler"])
    df["batter"] = df["batter"].astype(str).str.strip()
    df["bowler"] = df["bowler"].astype(str).str.strip()
    df["season"] = df["season"].astype(int)
    df["match_id"] = df["match_id"].astype(str).str.strip()
    df["innings_id"] = df["innings_id"].astype(str).str.extract(r"(\d+)", expand=False)
    df["innings_id"] = pd.to_numeric(df["innings_id"], errors="coerce")
    df["venue"] = df["venue"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    df["city"] = df["city"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    df["non_striker"] = df["non_striker"].astype(str).str.strip()
    df["batting_team"] = df["batting_team"].astype(str).str.strip()
    df["bowling_team"] = df["bowling_team"].astype(str).str.strip()
    df["team_a"] = df["team_a"].astype(str).str.strip()
    df["team_b"] = df["team_b"].astype(str).str.strip()
    df["wicket_fielders"] = df["wicket_fielders"].astype(str).str.strip()
    df["replacement_in"] = df["replacement_in"].astype(str).str.strip()
    df["replacements_out"] = df["replacements_out"].astype(str).str.strip()
    # Derive bowling team when dataset omits it (common in some schemas with team_a/team_b + batting_team).
    missing_bowling = df["bowling_team"].str.lower().isin({"", "nan", "none", "<na>"})
    team_a_valid = ~df["team_a"].str.lower().isin({"", "nan", "none", "<na>"})
    team_b_valid = ~df["team_b"].str.lower().isin({"", "nan", "none", "<na>"})
    batting_equals_a = df["batting_team"] == df["team_a"]
    batting_equals_b = df["batting_team"] == df["team_b"]
    df.loc[missing_bowling & batting_equals_a & team_b_valid, "bowling_team"] = df.loc[
        missing_bowling & batting_equals_a & team_b_valid, "team_b"
    ]
    df.loc[missing_bowling & batting_equals_b & team_a_valid, "bowling_team"] = df.loc[
        missing_bowling & batting_equals_b & team_a_valid, "team_a"
    ]
    df["match_date"] = pd.to_datetime(
        df["match_date_raw"].astype(str).str.extract(r"(\d{4}-\d{2}-\d{2})", expand=False),
        errors="coerce",
    )
    # Normalize inconsistent city labels for the same venue across seasons.
    maharaja_mask = df["venue"].str.contains("Maharaja Yadavindra Singh", case=False, na=False)
    df.loc[maharaja_mask, "city"] = "New Chandigarh"
    if df["total_runs"].isna().any():
        if df["extras"].notna().any():
            df["total_runs"] = df["total_runs"].fillna(df["runs"] + df["extras"])
        else:
            df["total_runs"] = df["total_runs"].fillna(df["runs"] + df["wides"] + df["noballs"])
    df["total_runs"] = df["total_runs"].fillna(0)
    # Batter does not face legal delivery on wides.
    df["balls_faced"] = (df["wides"] == 0).astype(int)
    # Bowler legal balls exclude wides and no-balls.
    df["balls_bowled"] = ((df["wides"] == 0) & (df["noballs"] == 0)).astype(int)

    return df


@st.cache_data(show_spinner=False)
def top_run_scorers(df: pd.DataFrame) -> pd.DataFrame:
    scorers = (
        df.groupby("batter", as_index=False)["runs"]
        .sum()
        .sort_values(["runs", "batter"], ascending=[False, True])
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    scorers["rank"] = scorers.index + 1
    return scorers[["rank", "batter", "runs"]]


@st.cache_data(show_spinner=False)
def top_wicket_takers(df: pd.DataFrame) -> pd.DataFrame:
    wickets = (
        df[df["wicket_kind"].isin(BOWLER_WICKET_KINDS)]
        .groupby("bowler", as_index=False)
        .size()
        .rename(columns={"size": "wickets"})
        .sort_values(["wickets", "bowler"], ascending=[False, True])
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    wickets["rank"] = wickets.index + 1
    return wickets[["rank", "bowler", "wickets"]]


@st.cache_data(show_spinner=False)
def top_run_scorers_by_phase(df: pd.DataFrame) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(columns=["phase", "rank", "batter", "runs"])

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )

    grouped = (
        phase_df.groupby(["phase", "batter"], as_index=False, observed=True)["runs"]
        .sum()
        .sort_values(["phase", "runs", "batter"], ascending=[True, False, True])
    )

    top_by_phase = grouped.groupby("phase", group_keys=False).head(TOP_N).copy()
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    return top_by_phase[["phase", "rank", "batter", "runs"]]


@st.cache_data(show_spinner=False)
def top_wicket_takers_by_phase(df: pd.DataFrame) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(columns=["phase", "rank", "bowler", "wickets"])

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )

    grouped = (
        phase_df[phase_df["wicket_kind"].isin(BOWLER_WICKET_KINDS)]
        .groupby(["phase", "bowler"], as_index=False, observed=True)
        .size()
        .rename(columns={"size": "wickets"})
        .sort_values(["phase", "wickets", "bowler"], ascending=[True, False, True])
    )

    top_by_phase = grouped.groupby("phase", group_keys=False).head(TOP_N).copy()
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    return top_by_phase[["phase", "rank", "bowler", "wickets"]]


@st.cache_data(show_spinner=False)
def top_batter_impact_by_phase(df: pd.DataFrame) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(columns=["phase", "rank", "batter", "runs", "balls", "strike_rate"])

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )

    grouped = (
        phase_df.groupby(["phase", "batter"], as_index=False, observed=True)
        .agg(runs=("runs", "sum"), balls=("balls_faced", "sum"))
    )
    grouped = grouped[grouped["balls"] >= 50].copy()
    grouped["strike_rate"] = (grouped["runs"] / grouped["balls"]) * 100

    top_by_phase = (
        grouped.sort_values(
            ["phase", "strike_rate", "runs", "balls", "batter"],
            ascending=[True, False, False, False, True],
        )
        .groupby("phase", group_keys=False)
        .head(TOP_N)
        .copy()
    )
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    top_by_phase["strike_rate"] = top_by_phase["strike_rate"].round(2)
    return top_by_phase[["phase", "rank", "batter", "runs", "balls", "strike_rate"]]


@st.cache_data(show_spinner=False)
def top_bowling_impact_by_phase(df: pd.DataFrame, min_balls_per_phase: int) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(
            columns=["phase", "rank", "bowler", "wickets", "balls", "wicket_per_ball"]
        )

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )
    phase_df["is_bowler_wicket"] = phase_df["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)

    grouped = (
        phase_df.groupby(["phase", "bowler"], as_index=False, observed=True)
        .agg(wickets=("is_bowler_wicket", "sum"), balls=("balls_bowled", "sum"))
    )
    grouped = grouped[grouped["balls"] >= min_balls_per_phase].copy()
    grouped["wicket_per_ball"] = grouped["wickets"] / grouped["balls"]

    top_by_phase = (
        grouped.sort_values(
            ["phase", "wicket_per_ball", "wickets", "balls", "bowler"],
            ascending=[True, False, False, False, True],
        )
        .groupby("phase", group_keys=False)
        .head(TOP_N)
        .copy()
    )
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    top_by_phase["wicket_per_ball"] = top_by_phase["wicket_per_ball"].round(4)
    return top_by_phase[["phase", "rank", "bowler", "wickets", "balls", "wicket_per_ball"]]


@st.cache_data(show_spinner=False)
def top_batter_innings_profile(df: pd.DataFrame) -> pd.DataFrame:
    if "match_id" not in df.columns or "innings_id" not in df.columns:
        return pd.DataFrame(
            columns=[
                "rank",
                "batter",
                "innings",
                "total_balls",
                "avg_balls_per_innings",
                "avg_runs_per_innings",
            ]
        )

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()

    batter_innings = (
        innings_df.groupby(["batter", "match_id", "innings_id"], as_index=False)
        .agg(innings_balls=("balls_faced", "sum"), innings_runs=("runs", "sum"))
    )
    batter_innings = batter_innings[batter_innings["innings_balls"] > 0].copy()
    if batter_innings.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "batter",
                "innings",
                "total_balls",
                "avg_balls_per_innings",
                "avg_runs_per_innings",
            ]
        )

    summary = (
        batter_innings.groupby("batter", as_index=False)
        .agg(
            innings=("innings_balls", "count"),
            total_balls=("innings_balls", "sum"),
            total_runs=("innings_runs", "sum"),
        )
    )
    summary = summary[summary["total_balls"] >= 100].copy()
    summary["avg_balls_per_innings"] = summary["total_balls"] / summary["innings"]
    summary["avg_runs_per_innings"] = summary["total_runs"] / summary["innings"]

    summary = (
        summary.sort_values(
            ["avg_balls_per_innings", "avg_runs_per_innings", "total_balls", "batter"],
            ascending=[False, False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    summary["rank"] = summary.index + 1
    summary["avg_balls_per_innings"] = summary["avg_balls_per_innings"].round(2)
    summary["avg_runs_per_innings"] = summary["avg_runs_per_innings"].round(2)

    return summary[
        [
            "rank",
            "batter",
            "innings",
            "total_balls",
            "avg_balls_per_innings",
            "avg_runs_per_innings",
        ]
    ]


@st.cache_data(show_spinner=False)
def top_dot_ball_pct_by_phase(df: pd.DataFrame, min_balls_per_phase: int) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(columns=["phase", "rank", "bowler", "dot_balls", "balls", "dot_ball_pct"])

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )
    phase_df["dot_ball"] = ((phase_df["balls_bowled"] == 1) & (phase_df["total_runs"] == 0)).astype(int)

    grouped = (
        phase_df.groupby(["phase", "bowler"], as_index=False, observed=True)
        .agg(dot_balls=("dot_ball", "sum"), balls=("balls_bowled", "sum"))
    )
    grouped = grouped[grouped["balls"] >= min_balls_per_phase].copy()
    grouped["dot_ball_pct"] = (grouped["dot_balls"] / grouped["balls"]) * 100

    top_by_phase = (
        grouped.sort_values(
            ["phase", "dot_ball_pct", "dot_balls", "balls", "bowler"],
            ascending=[True, False, False, False, True],
        )
        .groupby("phase", group_keys=False)
        .head(TOP_N)
        .copy()
    )
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    top_by_phase["dot_ball_pct"] = top_by_phase["dot_ball_pct"].round(2)
    return top_by_phase[["phase", "rank", "bowler", "dot_balls", "balls", "dot_ball_pct"]]


@st.cache_data(show_spinner=False)
def top_boundary_impact_by_phase(df: pd.DataFrame, min_balls_per_phase: int) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(
            columns=["phase", "rank", "batter", "boundaries", "balls", "boundary_rate"]
        )

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )
    phase_df["is_boundary"] = phase_df["runs"].isin([4, 6]).astype(int)

    grouped = (
        phase_df.groupby(["phase", "batter"], as_index=False, observed=True)
        .agg(boundaries=("is_boundary", "sum"), balls=("balls_faced", "sum"))
    )
    grouped = grouped[grouped["balls"] >= min_balls_per_phase].copy()
    # As requested: Boundaries hit / Balls faced.
    grouped["boundary_rate"] = grouped["boundaries"] / grouped["balls"]

    top_by_phase = (
        grouped.sort_values(
            ["phase", "boundary_rate", "boundaries", "balls", "batter"],
            ascending=[True, False, False, False, True],
        )
        .groupby("phase", group_keys=False)
        .head(TOP_N)
        .copy()
    )
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    top_by_phase["boundary_rate"] = top_by_phase["boundary_rate"].round(4)
    return top_by_phase[["phase", "rank", "batter", "boundaries", "balls", "boundary_rate"]]


@st.cache_data(show_spinner=False)
def top_bowling_avg_by_phase(df: pd.DataFrame, min_balls_per_phase: int) -> pd.DataFrame:
    phase_df = df[df["over_number"].between(1, 20, inclusive="both")].copy()
    if phase_df.empty:
        return pd.DataFrame(
            columns=["phase", "rank", "bowler", "runs_conceded", "wickets", "balls", "runs_per_wicket"]
        )

    phase_df["phase"] = pd.cut(
        phase_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )
    phase_df["is_bowler_wicket"] = phase_df["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)
    # Approximate bowler runs conceded (excludes byes/leg-byes where available in feed).
    phase_df["runs_conceded"] = phase_df["runs"] + phase_df["wides"] + phase_df["noballs"]

    grouped = (
        phase_df.groupby(["phase", "bowler"], as_index=False, observed=True)
        .agg(
            runs_conceded=("runs_conceded", "sum"),
            wickets=("is_bowler_wicket", "sum"),
            balls=("balls_bowled", "sum"),
        )
    )
    grouped = grouped[(grouped["balls"] >= min_balls_per_phase) & (grouped["wickets"] > 0)].copy()
    grouped["runs_per_wicket"] = grouped["runs_conceded"] / grouped["wickets"]

    top_by_phase = (
        grouped.sort_values(
            ["phase", "runs_per_wicket", "wickets", "balls", "bowler"],
            ascending=[True, True, False, False, True],
        )
        .groupby("phase", group_keys=False)
        .head(TOP_N)
        .copy()
    )
    top_by_phase["rank"] = top_by_phase.groupby("phase").cumcount() + 1
    top_by_phase["runs_per_wicket"] = top_by_phase["runs_per_wicket"].round(2)
    return top_by_phase[
        ["phase", "rank", "bowler", "runs_conceded", "wickets", "balls", "runs_per_wicket"]
    ]


@st.cache_data(show_spinner=False)
def top_batter_run_variance(df: pd.DataFrame, min_total_runs: int) -> pd.DataFrame:
    if "match_id" not in df.columns or "innings_id" not in df.columns:
        return pd.DataFrame(
            columns=["rank", "batter", "innings", "total_runs", "mean_runs", "run_variance"]
        )

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()

    batter_innings = (
        innings_df.groupby(["batter", "match_id", "innings_id"], as_index=False)
        .agg(innings_runs=("runs", "sum"))
    )
    if batter_innings.empty:
        return pd.DataFrame(
            columns=["rank", "batter", "innings", "total_runs", "mean_runs", "run_variance"]
        )

    summary = (
        batter_innings.groupby("batter", as_index=False)
        .agg(
            innings=("innings_runs", "count"),
            total_runs=("innings_runs", "sum"),
            mean_runs=("innings_runs", "mean"),
            run_variance=("innings_runs", "var"),
        )
    )
    summary["run_variance"] = summary["run_variance"].fillna(0)
    summary = summary[summary["total_runs"] > min_total_runs].copy()

    summary = (
        summary.sort_values(
            ["run_variance", "mean_runs", "total_runs", "batter"],
            ascending=[True, False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    summary["rank"] = summary.index + 1
    summary["mean_runs"] = summary["mean_runs"].round(2)
    summary["run_variance"] = summary["run_variance"].round(2)

    return summary[["rank", "batter", "innings", "total_runs", "mean_runs", "run_variance"]]


@st.cache_data(show_spinner=False)
def top_batter_30plus_counts(df: pd.DataFrame, min_total_runs: int) -> pd.DataFrame:
    if "match_id" not in df.columns or "innings_id" not in df.columns:
        return pd.DataFrame(
            columns=["rank", "batter", "total_runs", "innings", "scores_30_plus", "pct_30_plus"]
        )

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()

    batter_innings = (
        innings_df.groupby(["batter", "match_id", "innings_id"], as_index=False)
        .agg(innings_runs=("runs", "sum"))
    )
    if batter_innings.empty:
        return pd.DataFrame(
            columns=["rank", "batter", "total_runs", "innings", "scores_30_plus", "pct_30_plus"]
        )

    batter_innings["is_30_plus"] = (batter_innings["innings_runs"] >= 30).astype(int)
    summary = (
        batter_innings.groupby("batter", as_index=False)
        .agg(
            total_runs=("innings_runs", "sum"),
            innings=("innings_runs", "count"),
            scores_30_plus=("is_30_plus", "sum"),
        )
    )
    summary = summary[summary["total_runs"] >= min_total_runs].copy()
    summary["pct_30_plus"] = (summary["scores_30_plus"] / summary["innings"]) * 100

    summary = (
        summary.sort_values(
            ["pct_30_plus", "scores_30_plus", "total_runs", "innings", "batter"],
            ascending=[False, False, False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    summary["rank"] = summary.index + 1
    summary["pct_30_plus"] = summary["pct_30_plus"].round(2)
    return summary[["rank", "batter", "total_runs", "innings", "scores_30_plus", "pct_30_plus"]]


@st.cache_data(show_spinner=False)
def top_bowler_2w_innings_pct(df: pd.DataFrame, min_matches: int) -> pd.DataFrame:
    if "match_id" not in df.columns or "innings_id" not in df.columns:
        return pd.DataFrame(
            columns=[
                "rank",
                "bowler",
                "matches",
                "innings_bowled",
                "innings_2plus_wkts",
                "pct_2plus_wkt_innings",
            ]
        )

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()
    innings_df["is_bowler_wicket"] = innings_df["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)

    bowler_innings = (
        innings_df.groupby(["bowler", "match_id", "innings_id"], as_index=False)
        .agg(wickets_in_innings=("is_bowler_wicket", "sum"))
    )
    if bowler_innings.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "bowler",
                "matches",
                "innings_bowled",
                "innings_2plus_wkts",
                "pct_2plus_wkt_innings",
            ]
        )

    bowler_innings["is_2plus_wkts"] = (bowler_innings["wickets_in_innings"] >= 2).astype(int)
    summary = (
        bowler_innings.groupby("bowler", as_index=False)
        .agg(
            matches=("match_id", "nunique"),
            innings_bowled=("innings_id", "count"),
            innings_2plus_wkts=("is_2plus_wkts", "sum"),
        )
    )
    summary = summary[summary["matches"] >= min_matches].copy()
    summary["pct_2plus_wkt_innings"] = (
        summary["innings_2plus_wkts"] / summary["innings_bowled"]
    ) * 100

    summary = (
        summary.sort_values(
            ["pct_2plus_wkt_innings", "innings_2plus_wkts", "matches", "bowler"],
            ascending=[False, False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
        .copy()
    )
    summary["rank"] = summary.index + 1
    summary["pct_2plus_wkt_innings"] = summary["pct_2plus_wkt_innings"].round(2)
    return summary[
        [
            "rank",
            "bowler",
            "matches",
            "innings_bowled",
            "innings_2plus_wkts",
            "pct_2plus_wkt_innings",
        ]
    ]


@st.cache_data(show_spinner=False)
def franchise_player_participation(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "season",
        "match_id",
        "match_date",
        "batting_team",
        "bowling_team",
        "batter",
        "non_striker",
        "bowler",
    }
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["season", "match_id", "match_date", "franchise", "player"])

    base_cols = ["season", "match_id", "match_date"]
    batting_striker = df[base_cols + ["batting_team", "batter"]].rename(
        columns={"batting_team": "franchise", "batter": "player"}
    )
    batting_non_striker = df[base_cols + ["batting_team", "non_striker"]].rename(
        columns={"batting_team": "franchise", "non_striker": "player"}
    )
    bowling = df[base_cols + ["bowling_team", "bowler"]].rename(
        columns={"bowling_team": "franchise", "bowler": "player"}
    )
    # Fielders are part of the bowling side's XI and should count as appearances.
    fielders_rows = []
    if "wicket_fielders" in df.columns:
        fdf = df[base_cols + ["bowling_team", "wicket_fielders"]].copy()

        def _extract_names(raw: object) -> list[str]:
            if raw is None or (isinstance(raw, float) and pd.isna(raw)):
                return []
            text = str(raw).strip()
            if not text or text.lower() in {"nan", "<na>", "none"}:
                return []
            # Common format in this dataset: {"Name"} or {"Name A","Name B"}
            quoted = re.findall(r'"([^"]+)"', text)
            if quoted:
                return [q.strip() for q in quoted if q.strip()]
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, (set, list, tuple)):
                    return [str(x).strip() for x in parsed if str(x).strip()]
                if isinstance(parsed, str) and parsed.strip():
                    return [parsed.strip()]
            except Exception:
                pass
            return [text]

        for row in fdf.itertuples(index=False):
            for name in _extract_names(getattr(row, "wicket_fielders")):
                fielders_rows.append(
                    {
                        "season": getattr(row, "season"),
                        "match_id": getattr(row, "match_id"),
                        "match_date": getattr(row, "match_date"),
                        "franchise": getattr(row, "bowling_team"),
                        "player": name,
                    }
                )
    fielders = pd.DataFrame(fielders_rows)

    players = pd.concat([batting_striker, batting_non_striker, bowling, fielders], ignore_index=True)
    players["player"] = players["player"].astype(str).str.strip()
    players["franchise"] = players["franchise"].astype(str).str.strip()
    players["match_id"] = players["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    invalid = {"", "nan", "none", "<na>"}
    players = players[~players["player"].str.lower().isin(invalid)].copy()
    players = players[~players["franchise"].str.lower().isin(invalid)].copy()
    players = players.dropna(subset=["season", "match_id"]).drop_duplicates(
        subset=["season", "match_id", "franchise", "player"]
    )
    players["season"] = pd.to_numeric(players["season"], errors="coerce")
    players = players.dropna(subset=["season"]).copy()
    players["season"] = players["season"].astype(int)

    # Add impact-sub replacement appearances (replacement_in and replacements_out) with best-effort
    # franchise attribution using players already seen in the same match.
    if {"replacement_in", "replacements_out", "batting_team", "bowling_team"}.issubset(df.columns):
        invalid = {"", "nan", "none", "<na>"}
        base_match_map = (
            players.groupby(["season", "match_id", "player"])["franchise"]
            .agg(lambda s: sorted(set(x for x in s if str(x).strip())))
            .reset_index(name="known_franchises")
        )
        base_lookup = {
            (int(r.season), str(r.match_id), str(r.player)): r.known_franchises
            for r in base_match_map.itertuples(index=False)
        }

        repl_rows = []
        repl_df = df[
            [
                "season",
                "match_id",
                "match_date",
                "batting_team",
                "bowling_team",
                "replacement_in",
                "replacements_out",
            ]
        ].copy()
        repl_df["match_id"] = repl_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)

        for row in repl_df.itertuples(index=False):
            season = pd.to_numeric(getattr(row, "season"), errors="coerce")
            match_id = getattr(row, "match_id")
            if pd.isna(season) or not match_id:
                continue
            season = int(season)
            batting_team = str(getattr(row, "batting_team")).strip()
            bowling_team = str(getattr(row, "bowling_team")).strip()
            candidates = [t for t in [batting_team, bowling_team] if t and t.lower() not in invalid]

            names = []
            for raw_name in [getattr(row, "replacement_in"), getattr(row, "replacements_out")]:
                name = str(raw_name).strip()
                if name and name.lower() not in invalid:
                    names.append(name)

            if not names:
                continue

            # Infer one team for the replacement pair using existing match appearances.
            inferred_team = None
            for nm in names:
                known = base_lookup.get((season, str(match_id), nm), [])
                known_in_candidates = [k for k in known if k in candidates]
                if len(known_in_candidates) == 1:
                    inferred_team = known_in_candidates[0]
                    break

            # Fall back to batting_team if unresolved; this may still miss some bowling-side subs,
            # but resolved cases cover most practical mismatches when players also appear elsewhere.
            if inferred_team is None:
                inferred_team = candidates[0] if candidates else ""

            if not inferred_team or inferred_team.lower() in invalid:
                continue

            for nm in names:
                repl_rows.append(
                    {
                        "season": season,
                        "match_id": str(match_id),
                        "match_date": getattr(row, "match_date"),
                        "franchise": inferred_team,
                        "player": nm,
                    }
                )

        if repl_rows:
            repl_players = pd.DataFrame(repl_rows)
            players = pd.concat([players, repl_players], ignore_index=True)
            players["player"] = players["player"].astype(str).str.strip()
            players["franchise"] = players["franchise"].astype(str).str.strip()
            players = players[~players["player"].str.lower().isin(invalid)].copy()
            players = players[~players["franchise"].str.lower().isin(invalid)].copy()
            players = players.drop_duplicates(subset=["season", "match_id", "franchise", "player"]).reset_index(drop=True)

    return players.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def franchise_squad_consistency_summary(all_df: pd.DataFrame, focus_years: tuple[int, ...]) -> dict[str, pd.DataFrame]:
    players = franchise_player_participation(all_df)
    empty = pd.DataFrame()
    if players.empty:
        return {"yearly": empty, "combined": empty}

    min_year = min(focus_years)
    max_year = max(focus_years)
    players = players[players["season"].between(min_year - 1, max_year)].copy()

    match_key = players[["season", "franchise", "match_id", "match_date"]].drop_duplicates().copy()
    match_key["match_id_num"] = pd.to_numeric(match_key["match_id"], errors="coerce")
    ordered = match_key.sort_values(
        ["season", "franchise", "match_date", "match_id_num", "match_id"],
        ascending=[True, True, True, True, True],
        na_position="last",
    )
    first_matches = (
        ordered.groupby(["season", "franchise"], as_index=False).first()[["season", "franchise", "match_id"]]
        .rename(columns={"match_id": "first_match_id"})
    )
    last_matches = (
        ordered.groupby(["season", "franchise"], as_index=False).last()[["season", "franchise", "match_id"]]
        .rename(columns={"match_id": "last_match_id"})
    )

    games = (
        players.groupby(["season", "franchise", "player"], as_index=False)["match_id"]
        .nunique()
        .rename(columns={"match_id": "matches_played"})
    )

    yearly_parts: list[pd.DataFrame] = []
    available_all_years = set(players["season"].unique().tolist())
    for year in focus_years:
        yg = games[games["season"] == year].copy()
        if yg.empty:
            continue
        y_ten_plus_list = (
            yg[yg["matches_played"] >= 10]
            .groupby("franchise")["player"]
            .apply(lambda s: ", ".join(sorted(set(s))))
            .reset_index(name="Players with 10+ Games (List)")
        )
        y_summary = (
            yg.groupby("franchise", as_index=False)
            .agg(
                players_played=("player", "nunique"),
                players_10plus_games=("matches_played", lambda s: int((s >= 10).sum())),
            )
        )
        y_summary = y_summary.merge(y_ten_plus_list, on="franchise", how="left")
        y_summary["Players with 10+ Games (List)"] = (
            y_summary["Players with 10+ Games (List)"].fillna("")
        )
        y_summary["season"] = year
        retained_col = "Prev Season First-Game Players in Current Season Last Game"
        y_summary[retained_col] = 0
        prev_year = year - 1
        if prev_year in available_all_years:
            pf = first_matches[first_matches["season"] == prev_year][["franchise", "first_match_id"]]
            cl = last_matches[last_matches["season"] == year][["franchise", "last_match_id"]]
            pf_players = (
                players.merge(pf, left_on=["franchise", "match_id"], right_on=["franchise", "first_match_id"])
                [["franchise", "player"]]
                .drop_duplicates()
            )
            cl_players = (
                players.merge(cl, left_on=["franchise", "match_id"], right_on=["franchise", "last_match_id"])
                [["franchise", "player"]]
                .drop_duplicates()
            )
            retained = (
                pf_players.merge(cl_players, on=["franchise", "player"])
                .groupby("franchise", as_index=False)
                .size()
                .rename(columns={"size": retained_col})
            )
            y_summary = y_summary.drop(columns=[retained_col]).merge(retained, on="franchise", how="left")
            y_summary[retained_col] = y_summary[retained_col].fillna(0).astype(int)
        yearly_parts.append(y_summary)

    yearly = pd.concat(yearly_parts, ignore_index=True) if yearly_parts else empty
    if not yearly.empty:
        yearly = yearly.sort_values(["season", "franchise"]).reset_index(drop=True)

    fy = tuple(focus_years)
    focus_players = players[players["season"].isin(fy)].copy()
    combined = (
        focus_players.groupby("franchise", as_index=False)
        .agg(players_played_2023_2025=("player", "nunique"))
        .sort_values("franchise")
        .reset_index(drop=True)
    )

    focus_games = games[games["season"].isin(fy)].copy()
    per_player = (
        focus_games.groupby(["franchise", "player"], as_index=False)
        .agg(seasons_present=("season", "nunique"), min_games=("matches_played", "min"))
    )
    per_player = per_player[(per_player["seasons_present"] == len(fy)) & (per_player["min_games"] >= 10)].copy()
    per_player_summary = (
        per_player.groupby("franchise", as_index=False)
        .size()
        .rename(columns={"size": "players_10plus_games_each_season"})
    )
    per_player_list = (
        per_player.groupby("franchise")["player"]
        .apply(lambda s: ", ".join(sorted(set(s))))
        .reset_index(name="Players with 10+ Games in Each Season (List)")
    )
    combined = combined.merge(per_player_summary, on="franchise", how="left")
    combined = combined.merge(per_player_list, on="franchise", how="left")
    combined["players_10plus_games_each_season"] = (
        combined["players_10plus_games_each_season"].fillna(0).astype(int)
    )
    combined["Players with 10+ Games in Each Season (List)"] = (
        combined["Players with 10+ Games in Each Season (List)"].fillna("")
    )

    f2023 = first_matches[first_matches["season"] == min_year][["franchise", "first_match_id"]]
    l2025 = last_matches[last_matches["season"] == max_year][["franchise", "last_match_id"]]
    f2023_players = (
        players.merge(f2023, left_on=["franchise", "match_id"], right_on=["franchise", "first_match_id"])
        [["franchise", "player"]]
        .drop_duplicates()
    )
    l2025_players = (
        players.merge(l2025, left_on=["franchise", "match_id"], right_on=["franchise", "last_match_id"])
        [["franchise", "player"]]
        .drop_duplicates()
    )
    continuity = (
        f2023_players.merge(l2025_players, on=["franchise", "player"])
        .groupby("franchise", as_index=False)
        .size()
        .rename(columns={"size": "Played First Game 2023 and Last Game 2025"})
    )
    combined = combined.merge(continuity, on="franchise", how="left")
    combined["Played First Game 2023 and Last Game 2025"] = (
        combined["Played First Game 2023 and Last Game 2025"].fillna(0).astype(int)
    )

    return {"yearly": yearly, "combined": combined}


@st.cache_data(show_spinner=False)
def venue_innings_averages(df: pd.DataFrame) -> pd.DataFrame:
    if "venue" not in df.columns or "match_id" not in df.columns or "innings_id" not in df.columns:
        return pd.DataFrame()

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()
    innings_df["innings_id"] = pd.to_numeric(innings_df["innings_id"], errors="coerce")
    innings_df = innings_df[innings_df["innings_id"].isin([1, 2])].copy()
    if innings_df.empty:
        return pd.DataFrame()

    innings_df["is_boundary"] = innings_df["runs"].isin([4, 6]).astype(int)

    innings_totals = (
        innings_df.groupby(["venue", "city", "match_id", "innings_id"], as_index=False)
        .agg(
            innings_total=("total_runs", "sum"),
            boundaries=("is_boundary", "sum"),
        )
    )

    venue_avg = (
        innings_totals.groupby(["venue", "city", "innings_id"], as_index=False)
        .agg(
            innings_count=("match_id", "count"),
            avg_total_score=("innings_total", "mean"),
            avg_boundaries=("boundaries", "mean"),
        )
    )

    pivot = venue_avg.pivot(index=["venue", "city"], columns="innings_id")
    pivot.columns = [f"{metric}_inn{int(inn)}" for metric, inn in pivot.columns]
    pivot = pivot.reset_index()

    for col in [
        "innings_count_inn1",
        "innings_count_inn2",
        "avg_total_score_inn1",
        "avg_total_score_inn2",
        "avg_boundaries_inn1",
        "avg_boundaries_inn2",
    ]:
        if col not in pivot.columns:
            pivot[col] = pd.NA

    for col in ["avg_total_score_inn1", "avg_total_score_inn2", "avg_boundaries_inn1", "avg_boundaries_inn2"]:
        pivot[col] = pd.to_numeric(pivot[col], errors="coerce").round(2)

    return pivot.sort_values(
        ["avg_total_score_inn1", "venue"], ascending=[False, True], na_position="last"
    ).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def top_batters_by_venue(df: pd.DataFrame, min_innings_at_venue: int) -> pd.DataFrame:
    required = {"venue", "city", "match_id", "innings_id", "batter", "runs", "balls_faced"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    work = df.dropna(subset=["innings_id"]).copy()
    work["match_id"] = work["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    work = work.dropna(subset=["match_id"]).copy()
    work["is_boundary"] = work["runs"].isin([4, 6]).astype(int)

    batter_innings_venue = (
        work.groupby(["venue", "city", "batter", "match_id", "innings_id"], as_index=False)
        .agg(
            innings_runs=("runs", "sum"),
            innings_balls=("balls_faced", "sum"),
            innings_boundaries=("is_boundary", "sum"),
        )
    )
    batter_innings_venue = batter_innings_venue[batter_innings_venue["innings_balls"] > 0].copy()
    if batter_innings_venue.empty:
        return pd.DataFrame()

    summary = (
        batter_innings_venue.groupby(["venue", "city", "batter"], as_index=False)
        .agg(
            innings=("innings_runs", "count"),
            runs=("innings_runs", "sum"),
            balls=("innings_balls", "sum"),
            boundaries=("innings_boundaries", "sum"),
        )
    )
    summary = summary[summary["innings"] >= min_innings_at_venue].copy()
    if summary.empty:
        return pd.DataFrame()

    summary["avg_runs_per_innings"] = summary["runs"] / summary["innings"]
    summary["strike_rate"] = (summary["runs"] / summary["balls"]) * 100
    summary["balls_per_boundary"] = summary["balls"] / summary["boundaries"].replace(0, pd.NA)

    top3 = (
        summary.sort_values(
            ["venue", "avg_runs_per_innings", "runs", "strike_rate", "batter"],
            ascending=[True, False, False, False, True],
        )
        .groupby(["venue", "city"], group_keys=False)
        .head(3)
        .copy()
    )
    top3["rank_in_venue"] = top3.groupby(["venue", "city"]).cumcount() + 1
    for col in ["avg_runs_per_innings", "strike_rate", "balls_per_boundary"]:
        top3[col] = pd.to_numeric(top3[col], errors="coerce").round(2)

    return top3[
        [
            "venue",
            "city",
            "rank_in_venue",
            "batter",
            "innings",
            "runs",
            "avg_runs_per_innings",
            "strike_rate",
            "balls_per_boundary",
        ]
    ].sort_values(["venue", "rank_in_venue"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def home_batting_leaders(df: pd.DataFrame) -> pd.DataFrame:
    required = {"batting_team", "venue", "batter", "runs"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    home_rows = df[
        df.apply(
            lambda r: r["venue"] in HOME_VENUES_BY_FRANCHISE.get(r["batting_team"], set()),
            axis=1,
        )
    ].copy()
    if home_rows.empty:
        return pd.DataFrame()

    player_runs_sf = (
        home_rows.groupby(["season", "batting_team", "batter"], as_index=False)["runs"]
        .sum()
        .rename(columns={"batting_team": "franchise", "batter": "player", "runs": "home_runs"})
    )
    team_runs_sf = (
        home_rows.groupby(["season", "batting_team"], as_index=False)["runs"]
        .sum()
        .rename(columns={"batting_team": "franchise", "runs": "franchise_home_runs"})
    )

    # Denominator must be only for franchise-seasons where the player actually belonged to that franchise.
    participation = franchise_player_participation(df)
    player_franchise_seasons = participation[["season", "franchise", "player"]].drop_duplicates()
    denom = (
        player_franchise_seasons.merge(team_runs_sf, on=["season", "franchise"], how="left")
        .groupby("player", as_index=False)["franchise_home_runs"]
        .sum()
    )

    detail = (
        player_runs_sf.groupby(["franchise", "player"], as_index=False)["home_runs"]
        .sum()
    )
    detail["franchise_detail"] = detail.apply(
        lambda r: f"{r['franchise']} ({int(r['home_runs'])})", axis=1
    )
    out = detail.groupby("player", as_index=False).agg(
        home_runs=("home_runs", "sum"),
        franchise_breakdown=("franchise_detail", lambda s: ", ".join(sorted(set(s)))),
    )
    out = out.merge(denom, on="player", how="left")
    out["franchise_home_runs"] = pd.to_numeric(out["franchise_home_runs"], errors="coerce").fillna(0)
    out = out[out["franchise_home_runs"] > 0].copy()
    out["pct_of_franchise_home_runs"] = (out["home_runs"] / out["franchise_home_runs"]) * 100
    out["player_display"] = out["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(out["player"])
    out = (
        out.sort_values(
            ["home_runs", "pct_of_franchise_home_runs", "player_display"],
            ascending=[False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )
    out["rank"] = out.index + 1
    out["pct_of_franchise_home_runs"] = out["pct_of_franchise_home_runs"].round(2)
    return out[
        [
            "rank",
            "player_display",
            "franchise_breakdown",
            "home_runs",
            "franchise_home_runs",
            "pct_of_franchise_home_runs",
        ]
    ]


@st.cache_data(show_spinner=False)
def home_bowling_leaders(df: pd.DataFrame) -> pd.DataFrame:
    required = {"bowling_team", "venue", "bowler", "wicket_kind"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    home_rows = df[
        df.apply(
            lambda r: r["venue"] in HOME_VENUES_BY_FRANCHISE.get(r["bowling_team"], set()),
            axis=1,
        )
    ].copy()
    if home_rows.empty:
        return pd.DataFrame()

    home_rows["is_bowler_wicket"] = home_rows["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)
    player_wkts_sf = (
        home_rows.groupby(["season", "bowling_team", "bowler"], as_index=False)["is_bowler_wicket"]
        .sum()
        .rename(columns={"bowling_team": "franchise", "bowler": "player", "is_bowler_wicket": "home_wickets"})
    )
    team_wkts_sf = (
        home_rows.groupby(["season", "bowling_team"], as_index=False)["is_bowler_wicket"]
        .sum()
        .rename(columns={"bowling_team": "franchise", "is_bowler_wicket": "franchise_home_wickets"})
    )

    participation = franchise_player_participation(df)
    player_franchise_seasons = participation[["season", "franchise", "player"]].drop_duplicates()
    denom = (
        player_franchise_seasons.merge(team_wkts_sf, on=["season", "franchise"], how="left")
        .groupby("player", as_index=False)["franchise_home_wickets"]
        .sum()
    )

    detail = (
        player_wkts_sf.groupby(["franchise", "player"], as_index=False)["home_wickets"]
        .sum()
    )
    detail = detail[detail["home_wickets"] > 0].copy()
    detail["franchise_detail"] = detail.apply(
        lambda r: f"{r['franchise']} ({int(r['home_wickets'])})", axis=1
    )
    out = detail.groupby("player", as_index=False).agg(
        home_wickets=("home_wickets", "sum"),
        franchise_breakdown=("franchise_detail", lambda s: ", ".join(sorted(set(s)))),
    )
    out = out.merge(denom, on="player", how="left")
    out["franchise_home_wickets"] = pd.to_numeric(out["franchise_home_wickets"], errors="coerce").fillna(0)
    out = out[out["franchise_home_wickets"] > 0].copy()
    out["pct_of_franchise_home_wickets"] = (out["home_wickets"] / out["franchise_home_wickets"]) * 100
    out["player_display"] = out["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(out["player"])
    out = (
        out.sort_values(
            ["home_wickets", "pct_of_franchise_home_wickets", "player_display"],
            ascending=[False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )
    out["rank"] = out.index + 1
    out["pct_of_franchise_home_wickets"] = out["pct_of_franchise_home_wickets"].round(2)
    return out[
        [
            "rank",
            "player_display",
            "franchise_breakdown",
            "home_wickets",
            "franchise_home_wickets",
            "pct_of_franchise_home_wickets",
        ]
    ]


@st.cache_data(show_spinner=False)
def away_batting_leaders(df: pd.DataFrame) -> pd.DataFrame:
    required = {"batting_team", "venue", "batter", "runs", "season"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    away_rows = df[
        df.apply(
            lambda r: r["venue"] not in HOME_VENUES_BY_FRANCHISE.get(r["batting_team"], set()),
            axis=1,
        )
    ].copy()
    if away_rows.empty:
        return pd.DataFrame()

    player_runs_sf = (
        away_rows.groupby(["season", "batting_team", "batter"], as_index=False)["runs"]
        .sum()
        .rename(columns={"batting_team": "franchise", "batter": "player", "runs": "away_runs"})
    )
    team_runs_sf = (
        away_rows.groupby(["season", "batting_team"], as_index=False)["runs"]
        .sum()
        .rename(columns={"batting_team": "franchise", "runs": "franchise_away_runs"})
    )

    participation = franchise_player_participation(df)
    player_franchise_seasons = participation[["season", "franchise", "player"]].drop_duplicates()
    denom = (
        player_franchise_seasons.merge(team_runs_sf, on=["season", "franchise"], how="left")
        .groupby("player", as_index=False)["franchise_away_runs"]
        .sum()
    )

    detail = (
        player_runs_sf.groupby(["franchise", "player"], as_index=False)["away_runs"]
        .sum()
    )
    detail["franchise_detail"] = detail.apply(
        lambda r: f"{r['franchise']} ({int(r['away_runs'])})", axis=1
    )
    out = detail.groupby("player", as_index=False).agg(
        away_runs=("away_runs", "sum"),
        franchise_breakdown=("franchise_detail", lambda s: ", ".join(sorted(set(s)))),
    )
    out = out.merge(denom, on="player", how="left")
    out["franchise_away_runs"] = pd.to_numeric(out["franchise_away_runs"], errors="coerce").fillna(0)
    out = out[out["franchise_away_runs"] > 0].copy()
    out["pct_of_franchise_away_runs"] = (out["away_runs"] / out["franchise_away_runs"]) * 100
    out["player_display"] = out["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(out["player"])
    out = (
        out.sort_values(
            ["away_runs", "pct_of_franchise_away_runs", "player_display"],
            ascending=[False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )
    out["rank"] = out.index + 1
    out["pct_of_franchise_away_runs"] = out["pct_of_franchise_away_runs"].round(2)
    return out[
        [
            "rank",
            "player_display",
            "franchise_breakdown",
            "away_runs",
            "franchise_away_runs",
            "pct_of_franchise_away_runs",
        ]
    ]


@st.cache_data(show_spinner=False)
def away_bowling_leaders(df: pd.DataFrame) -> pd.DataFrame:
    required = {"bowling_team", "venue", "bowler", "wicket_kind", "season"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    away_rows = df[
        df.apply(
            lambda r: r["venue"] not in HOME_VENUES_BY_FRANCHISE.get(r["bowling_team"], set()),
            axis=1,
        )
    ].copy()
    if away_rows.empty:
        return pd.DataFrame()

    away_rows["is_bowler_wicket"] = away_rows["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)
    player_wkts_sf = (
        away_rows.groupby(["season", "bowling_team", "bowler"], as_index=False)["is_bowler_wicket"]
        .sum()
        .rename(columns={"bowling_team": "franchise", "bowler": "player", "is_bowler_wicket": "away_wickets"})
    )
    team_wkts_sf = (
        away_rows.groupby(["season", "bowling_team"], as_index=False)["is_bowler_wicket"]
        .sum()
        .rename(columns={"bowling_team": "franchise", "is_bowler_wicket": "franchise_away_wickets"})
    )

    participation = franchise_player_participation(df)
    player_franchise_seasons = participation[["season", "franchise", "player"]].drop_duplicates()
    denom = (
        player_franchise_seasons.merge(team_wkts_sf, on=["season", "franchise"], how="left")
        .groupby("player", as_index=False)["franchise_away_wickets"]
        .sum()
    )

    detail = (
        player_wkts_sf.groupby(["franchise", "player"], as_index=False)["away_wickets"]
        .sum()
    )
    detail = detail[detail["away_wickets"] > 0].copy()
    detail["franchise_detail"] = detail.apply(
        lambda r: f"{r['franchise']} ({int(r['away_wickets'])})", axis=1
    )
    out = detail.groupby("player", as_index=False).agg(
        away_wickets=("away_wickets", "sum"),
        franchise_breakdown=("franchise_detail", lambda s: ", ".join(sorted(set(s)))),
    )
    out = out.merge(denom, on="player", how="left")
    out["franchise_away_wickets"] = pd.to_numeric(out["franchise_away_wickets"], errors="coerce").fillna(0)
    out = out[out["franchise_away_wickets"] > 0].copy()
    out["pct_of_franchise_away_wickets"] = (out["away_wickets"] / out["franchise_away_wickets"]) * 100
    out["player_display"] = out["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(out["player"])
    out = (
        out.sort_values(
            ["away_wickets", "pct_of_franchise_away_wickets", "player_display"],
            ascending=[False, False, True],
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )
    out["rank"] = out.index + 1
    out["pct_of_franchise_away_wickets"] = out["pct_of_franchise_away_wickets"].round(2)
    return out[
        [
            "rank",
            "player_display",
            "franchise_breakdown",
            "away_wickets",
            "franchise_away_wickets",
            "pct_of_franchise_away_wickets",
        ]
    ]


@st.cache_data(show_spinner=False)
def batter_home_away_variance_summary(df: pd.DataFrame) -> pd.DataFrame:
    required = {"season", "batting_team", "venue", "batter", "runs"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    season_runs = (
        df.groupby(["batter", "season"], as_index=False)["runs"]
        .sum()
        .rename(columns={"batter": "player", "runs": "season_runs"})
    )
    if season_runs.empty:
        return pd.DataFrame()

    eligible = (
        season_runs.groupby("player")["season_runs"]
        .apply(lambda s: bool((s >= 300).all()))
        .reset_index(name="eligible")
    )
    eligible_players = set(eligible[eligible["eligible"]]["player"].tolist())
    if not eligible_players:
        return pd.DataFrame()

    work = df[df["batter"].isin(eligible_players)].copy()
    work["is_home"] = work.apply(
        lambda r: r["venue"] in HOME_VENUES_BY_FRANCHISE.get(r["batting_team"], set()),
        axis=1,
    )
    work["home_runs_part"] = work["runs"].where(work["is_home"], 0)
    work["away_runs_part"] = work["runs"].where(~work["is_home"], 0)

    summary = (
        work.groupby("batter", as_index=False)
        .agg(
            total_runs=("runs", "sum"),
            home_runs=("home_runs_part", "sum"),
            away_runs=("away_runs_part", "sum"),
        )
        .rename(columns={"batter": "player"})
    )
    seasons_played = (
        season_runs[season_runs["player"].isin(eligible_players)]
        .groupby("player", as_index=False)["season"]
        .nunique()
        .rename(columns={"season": "seasons_played"})
    )
    summary = summary.merge(seasons_played, on="player", how="left")
    summary["variance_home_away_runs"] = (summary["home_runs"] - summary["away_runs"]).abs()
    summary["norm_variance_home_away_runs"] = (
        summary["variance_home_away_runs"] / summary["total_runs"].replace(0, pd.NA)
    )
    summary["player_display"] = summary["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(summary["player"])
    summary["norm_variance_home_away_runs"] = pd.to_numeric(
        summary["norm_variance_home_away_runs"], errors="coerce"
    ).round(4)
    return summary[
        [
            "player",
            "player_display",
            "seasons_played",
            "total_runs",
            "home_runs",
            "away_runs",
            "variance_home_away_runs",
            "norm_variance_home_away_runs",
        ]
    ]


@st.cache_data(show_spinner=False)
def bowler_home_away_variance_summary(df: pd.DataFrame) -> pd.DataFrame:
    required = {"season", "bowling_team", "venue", "bowler", "wicket_kind"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    work = df.copy()
    work["is_w"] = work["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)

    season_wkts = (
        work.groupby(["bowler", "season"], as_index=False)["is_w"]
        .sum()
        .rename(columns={"bowler": "player", "is_w": "season_wickets"})
    )
    if season_wkts.empty:
        return pd.DataFrame()

    eligible = (
        season_wkts.groupby("player")["season_wickets"]
        .apply(lambda s: bool((s >= 10).all()))
        .reset_index(name="eligible")
    )
    eligible_players = set(eligible[eligible["eligible"]]["player"].tolist())
    if not eligible_players:
        return pd.DataFrame()

    work = work[work["bowler"].isin(eligible_players)].copy()
    work["is_home"] = work.apply(
        lambda r: r["venue"] in HOME_VENUES_BY_FRANCHISE.get(r["bowling_team"], set()),
        axis=1,
    )
    work["home_w_part"] = work["is_w"].where(work["is_home"], 0)
    work["away_w_part"] = work["is_w"].where(~work["is_home"], 0)

    summary = (
        work.groupby("bowler", as_index=False)
        .agg(
            total_wickets=("is_w", "sum"),
            home_wickets=("home_w_part", "sum"),
            away_wickets=("away_w_part", "sum"),
        )
        .rename(columns={"bowler": "player"})
    )
    seasons_played = (
        season_wkts[season_wkts["player"].isin(eligible_players)]
        .groupby("player", as_index=False)["season"]
        .nunique()
        .rename(columns={"season": "seasons_played"})
    )
    summary = summary.merge(seasons_played, on="player", how="left")
    summary["variance_home_away_wickets"] = (summary["home_wickets"] - summary["away_wickets"]).abs()
    summary["norm_variance_home_away_wickets"] = (
        summary["variance_home_away_wickets"] / summary["total_wickets"].replace(0, pd.NA)
    )
    summary["player_display"] = summary["player"].map(PLAYER_DISPLAY_OVERRIDES).fillna(summary["player"])
    summary["norm_variance_home_away_wickets"] = pd.to_numeric(
        summary["norm_variance_home_away_wickets"], errors="coerce"
    ).round(4)
    return summary[
        [
            "player",
            "player_display",
            "seasons_played",
            "total_wickets",
            "home_wickets",
            "away_wickets",
            "variance_home_away_wickets",
            "norm_variance_home_away_wickets",
        ]
    ]


def _add_venue_score_trend_columns(
    current_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    *,
    first_col_name: str,
    second_col_name: str,
) -> pd.DataFrame:
    if current_df.empty:
        return current_df.copy()

    result = current_df.copy()
    result[first_col_name] = pd.NA
    result[second_col_name] = pd.NA

    if reference_df.empty:
        return result

    join_cols = ["venue", "city"]
    ref = reference_df[
        [*join_cols, "avg_total_score_inn1", "avg_total_score_inn2"]
    ].rename(
        columns={
            "avg_total_score_inn1": "ref_avg_total_score_inn1",
            "avg_total_score_inn2": "ref_avg_total_score_inn2",
        }
    )
    merged = result.merge(ref, on=join_cols, how="left")

    delta1 = merged["avg_total_score_inn1"] - merged["ref_avg_total_score_inn1"]
    delta2 = merged["avg_total_score_inn2"] - merged["ref_avg_total_score_inn2"]
    merged[first_col_name] = delta1.round(2)
    merged[second_col_name] = delta2.round(2)

    return merged.drop(columns=["ref_avg_total_score_inn1", "ref_avg_total_score_inn2"])


@st.cache_data(show_spinner=False)
def scope_milestone_summary(df: pd.DataFrame) -> dict[str, int]:
    if "match_id" not in df.columns or "innings_id" not in df.columns:
        return {
            "50_plus_scores": 0,
            "100_plus_scores": 0,
            "two_plus_wicket_hauls": 0,
            "four_plus_wicket_hauls": 0,
        }

    innings_df = df.dropna(subset=["innings_id"]).copy()
    innings_df["match_id"] = innings_df["match_id"].astype(str).str.extract(r"(\d+)", expand=False)
    innings_df = innings_df.dropna(subset=["match_id"]).copy()
    innings_df["is_bowler_wicket"] = innings_df["wicket_kind"].isin(BOWLER_WICKET_KINDS).astype(int)

    batter_innings = (
        innings_df.groupby(["batter", "match_id", "innings_id"], as_index=False)
        .agg(innings_runs=("runs", "sum"))
    )
    bowler_innings = (
        innings_df.groupby(["bowler", "match_id", "innings_id"], as_index=False)
        .agg(wickets=("is_bowler_wicket", "sum"))
    )

    return {
        "50_plus_scores": int((batter_innings["innings_runs"] >= 50).sum()) if not batter_innings.empty else 0,
        "100_plus_scores": int((batter_innings["innings_runs"] >= 100).sum()) if not batter_innings.empty else 0,
        "two_plus_wicket_hauls": int((bowler_innings["wickets"] >= 2).sum()) if not bowler_innings.empty else 0,
        "four_plus_wicket_hauls": int((bowler_innings["wickets"] >= 4).sum()) if not bowler_innings.empty else 0,
    }


@st.cache_data(show_spinner=False)
def batter_position_and_phase_summary(df: pd.DataFrame, batter_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_cols = {"season", "match_id", "innings_id", "batter", "runs", "balls_faced", "over_number"}
    if not required_cols.issubset(df.columns):
        return (
            pd.DataFrame(columns=["position", "innings", "runs", "balls", "strike_rate"]),
            pd.DataFrame(columns=["phase", "runs", "balls", "strike_rate"]),
        )

    scoped = df.copy().reset_index(drop=False).rename(columns={"index": "_row_order"})
    innings_cols = ["season", "match_id", "innings_id"]
    scoped = scoped.dropna(subset=innings_cols + ["batter"]).copy()
    player_ball_df = scoped[scoped["batter"] == batter_name].copy()
    if player_ball_df.empty:
        return (
            pd.DataFrame(columns=["position", "innings", "runs", "balls", "strike_rate"]),
            pd.DataFrame(columns=["phase", "runs", "balls", "strike_rate"]),
        )

    batter_events = scoped[innings_cols + ["over_number", "_row_order", "batter"]].rename(
        columns={"batter": "player"}
    )
    non_striker_events = scoped[innings_cols + ["over_number", "_row_order", "non_striker"]].rename(
        columns={"non_striker": "player"}
    )
    events = pd.concat([batter_events, non_striker_events], ignore_index=True)
    events["player"] = events["player"].astype(str).str.strip()
    events = events[~events["player"].str.lower().isin({"", "nan", "none", "<na>"})].copy()

    first_appearance = (
        events.sort_values(innings_cols + ["over_number", "_row_order", "player"])
        .drop_duplicates(innings_cols + ["player"], keep="first")
        .copy()
    )
    first_appearance["position"] = first_appearance.groupby(innings_cols).cumcount() + 1

    player_innings = first_appearance[first_appearance["player"] == batter_name][innings_cols + ["position"]].copy()
    player_ball_df = player_ball_df.merge(player_innings, on=innings_cols, how="left")
    player_ball_df = player_ball_df.dropna(subset=["position"]).copy()
    if player_ball_df.empty:
        return (
            pd.DataFrame(columns=["position", "innings", "runs", "balls", "strike_rate"]),
            pd.DataFrame(columns=["phase", "runs", "balls", "strike_rate"]),
        )

    player_ball_df["position"] = player_ball_df["position"].astype(int)
    player_ball_df["innings_key"] = (
        player_ball_df["season"].astype(str)
        + "_"
        + player_ball_df["match_id"].astype(str)
        + "_"
        + player_ball_df["innings_id"].astype(str)
    )

    position_table = (
        player_ball_df.groupby("position", as_index=False)
        .agg(
            innings=("innings_key", "nunique"),
            runs=("runs", "sum"),
            balls=("balls_faced", "sum"),
        )
        .sort_values("position")
        .reset_index(drop=True)
    )
    position_table["strike_rate"] = (
        (position_table["runs"] / position_table["balls"].replace(0, pd.NA)) * 100
    ).round(2)

    player_ball_df["phase"] = pd.cut(
        player_ball_df["over_number"],
        bins=[0, 6, 14, 20],
        labels=PHASE_ORDER,
        include_lowest=True,
    )
    phase_table = (
        player_ball_df.dropna(subset=["phase"])
        .groupby("phase", as_index=False, observed=True)
        .agg(runs=("runs", "sum"), balls=("balls_faced", "sum"))
    )
    phase_table["phase"] = pd.Categorical(phase_table["phase"], PHASE_ORDER, ordered=True)
    phase_table = phase_table.sort_values("phase").reset_index(drop=True)
    phase_table["strike_rate"] = ((phase_table["runs"] / phase_table["balls"].replace(0, pd.NA)) * 100).round(2)

    return position_table, phase_table


def render_main_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Top 20 Runs and Wickets")
    season_scope = st.radio(
        "Season scope",
        ["All (2023-2025 combined)", "Single season"],
        index=0,
        horizontal=True,
        key="main_scope",
    )

    if season_scope == "Single season":
        selected_year = st.selectbox(
            "Choose season",
            available_years,
            index=len(available_years) - 1,
            key="main_year",
        )
        scoped_df = focus_df[focus_df["season"] == selected_year].copy()
        st.caption(f"Showing season: {selected_year}")
    else:
        scoped_df = focus_df
        st.caption("Showing combined seasons: 2023-2025")

    runs_table = top_run_scorers(scoped_df).rename(
        columns={"rank": "Rank", "batter": "Batter", "runs": "Runs"}
    )
    wickets_table = top_wicket_takers(scoped_df).rename(
        columns={"rank": "Rank", "bowler": "Bowler", "wickets": "Wickets"}
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### Top 20 Run Scorers")
        st.dataframe(runs_table, use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Top 20 Wicket Takers")
        st.dataframe(wickets_table, use_container_width=True, hide_index=True)


def render_nehal_batter_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Summary - Nehal Wadhera")
    st.caption(
        "Year-wise and consolidated summary for runs and strike rate by batting position and phase "
        "(Overs 1-6, Overs 7-14, Overs 15-20)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            position_table, phase_table = batter_position_and_phase_summary(scoped_df, NEHAL_BATTER_NAME)
            if position_table.empty and phase_table.empty:
                st.warning(f"No batting records found for {NEHAL_BATTER_LABEL} in {year}.")
                continue
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

    with scope_tabs[-1]:
        position_table, phase_table = batter_position_and_phase_summary(focus_df, NEHAL_BATTER_NAME)
        if position_table.empty and phase_table.empty:
            st.warning(f"No batting records found for {NEHAL_BATTER_LABEL} in 2023-2025.")
        else:
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )


def render_naman_batter_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Summary - Naman Dhir")
    st.caption(
        "Year-wise and consolidated summary for runs and strike rate by batting position and phase "
        "(Overs 1-6, Overs 7-14, Overs 15-20)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            position_table, phase_table = batter_position_and_phase_summary(scoped_df, NAMAN_BATTER_NAME)
            if position_table.empty and phase_table.empty:
                st.warning(f"No batting records found for {NAMAN_BATTER_LABEL} in {year}.")
                continue
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

    with scope_tabs[-1]:
        position_table, phase_table = batter_position_and_phase_summary(focus_df, NAMAN_BATTER_NAME)
        if position_table.empty and phase_table.empty:
            st.warning(f"No batting records found for {NAMAN_BATTER_LABEL} in 2023-2025.")
        else:
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )


def render_angkrish_batter_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Summary - Angkrish Raghuvanshi")
    st.caption(
        "Year-wise and consolidated summary for runs and strike rate by batting position and phase "
        "(Overs 1-6, Overs 7-14, Overs 15-20)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            position_table, phase_table = batter_position_and_phase_summary(scoped_df, ANGKRISH_BATTER_NAME)
            if position_table.empty and phase_table.empty:
                st.warning(f"No batting records found for {ANGKRISH_BATTER_LABEL} in {year}.")
                continue
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

    with scope_tabs[-1]:
        position_table, phase_table = batter_position_and_phase_summary(focus_df, ANGKRISH_BATTER_NAME)
        if position_table.empty and phase_table.empty:
            st.warning(f"No batting records found for {ANGKRISH_BATTER_LABEL} in 2023-2025.")
        else:
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )


def render_ayush_batter_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Summary - Ayush Badoni")
    st.caption(
        "Year-wise and consolidated summary for runs and strike rate by batting position and phase "
        "(Overs 1-6, Overs 7-14, Overs 15-20)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            position_table, phase_table = batter_position_and_phase_summary(scoped_df, AYUSH_BATTER_NAME)
            if position_table.empty and phase_table.empty:
                st.warning(f"No batting records found for {AYUSH_BATTER_LABEL} in {year}.")
                continue
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

    with scope_tabs[-1]:
        position_table, phase_table = batter_position_and_phase_summary(focus_df, AYUSH_BATTER_NAME)
        if position_table.empty and phase_table.empty:
            st.warning(f"No batting records found for {AYUSH_BATTER_LABEL} in 2023-2025.")
        else:
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )


def render_dewald_batter_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Summary - Dewald Brevis")
    st.caption(
        "Year-wise and consolidated summary for runs and strike rate by batting position and phase "
        "(Overs 1-6, Overs 7-14, Overs 15-20)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            position_table, phase_table = batter_position_and_phase_summary(scoped_df, DEWALD_BATTER_NAME)
            if position_table.empty and phase_table.empty:
                st.warning(f"No batting records found for {DEWALD_BATTER_LABEL} in {year}.")
                continue
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

    with scope_tabs[-1]:
        position_table, phase_table = batter_position_and_phase_summary(focus_df, DEWALD_BATTER_NAME)
        if position_table.empty and phase_table.empty:
            st.warning(f"No batting records found for {DEWALD_BATTER_LABEL} in 2023-2025.")
        else:
            left, right = st.columns(2)
            with left:
                st.markdown("### Runs by Batting Position")
                if position_table.empty:
                    st.info("No batting-position data for this scope.")
                else:
                    st.dataframe(
                        position_table.rename(
                            columns={
                                "position": "Position",
                                "innings": "Innings",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with right:
                st.markdown("### Runs by Phase")
                if phase_table.empty:
                    st.info("No phase data for this scope.")
                else:
                    st.dataframe(
                        phase_table.rename(
                            columns={
                                "phase": "Phase",
                                "runs": "Runs",
                                "balls": "Balls",
                                "strike_rate": "Strike Rate",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )


def render_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Top 20 Run Getters by Phase")
    st.caption("Phases: Overs 1-6, Overs 7-14, Overs 15-20")

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_run_scorers_by_phase(scoped_df)
            render_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_run_scorers_by_phase(focus_df)
        render_phase_tables(phase_table, "Seasons 2023-2025")


def render_phase_wicket_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Top 20 Wicket Takers by Phase")
    st.caption("Phases: Overs 1-6, Overs 7-14, Overs 15-20")

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_wicket_takers_by_phase(scoped_df)
            render_phase_wicket_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_wicket_takers_by_phase(focus_df)
        render_phase_wicket_tables(phase_table, "Seasons 2023-2025")


def render_batter_impact_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Impact by Phase")
    st.caption("Top 20 batters by strike rate: (Runs scored / Balls faced) * 100")

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_batter_impact_by_phase(scoped_df)
            render_batter_impact_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_batter_impact_by_phase(focus_df)
        render_batter_impact_phase_tables(phase_table, "Seasons 2023-2025")


def render_bowling_impact_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Bowling Impact by Phase")
    st.caption(
        "Top 20 bowlers by bowling strike rate: wickets taken / balls bowled. "
        "Min balls per phase: 60 (yearly), 180 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_bowling_impact_by_phase(scoped_df, min_balls_per_phase=60)
            render_bowling_impact_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_bowling_impact_by_phase(focus_df, min_balls_per_phase=180)
        render_bowling_impact_phase_tables(phase_table, "Seasons 2023-2025")


def render_batter_innings_summary(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batter Innings Summary")
    st.caption(
        "Top 20 batters by average balls batted per innings. "
        "Minimum 100 balls faced in selected scope."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            summary_table = top_batter_innings_profile(scoped_df)
            render_batter_innings_summary_table(summary_table, f"Season {year}")

    with scope_tabs[-1]:
        summary_table = top_batter_innings_profile(focus_df)
        render_batter_innings_summary_table(summary_table, "Seasons 2023-2025")


def render_dot_ball_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Dot Ball % by Phase")
    st.caption(
        "Top 20 bowlers by dot ball percentage: dot balls / balls bowled. "
        "Min balls per phase: 60 (yearly), 180 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_dot_ball_pct_by_phase(scoped_df, min_balls_per_phase=60)
            render_dot_ball_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_dot_ball_pct_by_phase(focus_df, min_balls_per_phase=180)
        render_dot_ball_phase_tables(phase_table, "Seasons 2023-2025")


def render_boundary_impact_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Boundary Impact by Phase")
    st.caption(
        "Top 20 batters by boundaries hit / balls faced. "
        "Boundary = 4 or 6. Min balls per phase: 60 (yearly), 180 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_boundary_impact_by_phase(scoped_df, min_balls_per_phase=60)
            render_boundary_impact_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_boundary_impact_by_phase(focus_df, min_balls_per_phase=180)
        render_boundary_impact_phase_tables(phase_table, "Seasons 2023-2025")


def render_bowling_avg_phase_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Runs Conceded per Wicket by Phase")
    st.caption(
        "Top 20 bowlers by (runs conceded / wickets taken), ranked ascending. "
        "Min balls per phase: 60 (yearly), 180 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_bowling_avg_by_phase(scoped_df, min_balls_per_phase=60)
            render_bowling_avg_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_bowling_avg_by_phase(focus_df, min_balls_per_phase=180)
        render_bowling_avg_phase_tables(phase_table, "Seasons 2023-2025")


def render_batter_variance_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Batting Run Variance")
    st.caption(
        "Top 20 batters sorted by least variance in runs per innings. "
        "Minimum runs: >250 (yearly), >600 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            variance_table = top_batter_run_variance(scoped_df, min_total_runs=250)
            render_batter_variance_table(variance_table, f"Season {year}")

    with scope_tabs[-1]:
        variance_table = top_batter_run_variance(focus_df, min_total_runs=600)
        render_batter_variance_table(variance_table, "Seasons 2023-2025")


def render_batter_30plus_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("30+ Scores by Batter")
    st.caption(
        "Top 20 batters by number of innings with 30+ runs. "
        "Minimum runs: >=250 (yearly), >=600 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            summary_table = top_batter_30plus_counts(scoped_df, min_total_runs=250)
            render_batter_30plus_table(summary_table, f"Season {year}")

    with scope_tabs[-1]:
        summary_table = top_batter_30plus_counts(focus_df, min_total_runs=600)
        render_batter_30plus_table(summary_table, "Seasons 2023-2025")


def render_bowler_2w_leaderboards(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("2+ Wicket Innings %")
    st.caption(
        "Top 20 bowlers by % of innings with 2 or more wickets. "
        "Minimum matches: >=7 (yearly), >=18 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            summary_table = top_bowler_2w_innings_pct(scoped_df, min_matches=7)
            render_bowler_2w_table(summary_table, f"Season {year}")

    with scope_tabs[-1]:
        summary_table = top_bowler_2w_innings_pct(focus_df, min_matches=18)
        render_bowler_2w_table(summary_table, "Seasons 2023-2025")


def render_venue_summary_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Venue Scoring & Milestone Summary")
    st.caption(
        "Venue table shows average total scores and average boundaries (4s+6s) separately "
        "for 1st and 2nd innings. Metrics summarize milestone counts for the selected scope."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            prev_year_df = (
                focus_df[focus_df["season"] == year - 1].copy()
                if (year - 1) in available_years
                else pd.DataFrame()
            )
            render_venue_and_milestones(
                scoped_df,
                f"Season {year}",
                trend_reference_df=prev_year_df,
                trend_label_first="1st Inns Trend vs Prev Year",
                trend_label_second="2nd Inns Trend vs Prev Year",
            )

    with scope_tabs[-1]:
        start_year_df = focus_df[focus_df["season"] == 2023].copy()
        end_year_df = focus_df[focus_df["season"] == 2025].copy()
        render_venue_and_milestones(
            focus_df,
            "Seasons 2023-2025",
            trend_reference_df=start_year_df,
            trend_compare_df=end_year_df,
            trend_label_first="1st Inns Trend (2025 vs 2023)",
            trend_label_second="2nd Inns Trend (2025 vs 2023)",
        )


def render_franchise_squad_consistency_tab(raw_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Franchise Squad Consistency")
    st.caption(
        "Franchise-wise squad selection summary based on inferred player participation "
        "from ball-by-ball data (batter, non-striker, bowler appearances)."
    )

    summary = franchise_squad_consistency_summary(raw_df, tuple(FOCUS_YEARS))
    yearly = summary["yearly"]
    combined = summary["combined"]
    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            year_df = yearly[yearly["season"] == year].copy() if not yearly.empty else pd.DataFrame()
            if year_df.empty:
                st.warning(f"No franchise consistency summary available for {year}.")
                continue
            display_df = (
                year_df.drop(columns=["season"])
                .rename(
                    columns={
                        "franchise": "Franchise",
                        "players_played": "Players Used",
                        "players_10plus_games": "Players with 10+ Games",
                        "Players with 10+ Games (List)": "Players with 10+ Games (List)",
                    }
                )
                .sort_values(["Players Used", "Franchise"], ascending=[True, True])
                .reset_index(drop=True)
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    with scope_tabs[-1]:
        if combined.empty:
            st.warning("No consolidated franchise consistency summary available for 2023-2025.")
        else:
            display_df = combined.rename(
                columns={
                    "franchise": "Franchise",
                    "players_played_2023_2025": "Players Used (2023-2025)",
                    "players_10plus_games_each_season": "Players with 10+ Games in Each Season",
                    "Players with 10+ Games in Each Season (List)": "Players with 10+ Games in Each Season (List)",
                }
            ).sort_values(["Players Used (2023-2025)", "Franchise"], ascending=[True, True]).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_best_batters_by_venue_tab(focus_df: pd.DataFrame, available_years: list[int]) -> None:
    st.subheader("Best Batters by Venue")
    st.caption(
        "Top 3 batters at each venue ranked by average runs per innings. "
        "Metrics shown: total runs, average runs/innings, strike rate, balls per boundary. "
        "Min innings at venue: 2 (yearly), 5 (combined)."
    )

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            table = top_batters_by_venue(scoped_df, min_innings_at_venue=2)
            render_best_batters_by_venue_table(table, f"Season {year}")

    with scope_tabs[-1]:
        table = top_batters_by_venue(focus_df, min_innings_at_venue=5)
        render_best_batters_by_venue_table(table, "Seasons 2023-2025")


def render_home_performance_tabs(focus_df: pd.DataFrame) -> None:
    st.subheader("Home Ground Leaders (2023-2025 Combined)")
    st.caption(
        "Franchise-specific home venue mapping is used per match, so player transfers across seasons "
        "are handled with their new franchise home venues."
    )

    batting = home_batting_leaders(focus_df)
    bowling = home_bowling_leaders(focus_df)
    left, right = st.columns(2)

    with left:
        st.markdown("### Top 20 Batters at Home")
        if batting.empty:
            st.warning("No eligible home batting data.")
        else:
            st.dataframe(
                batting.rename(
                    columns={
                        "rank": "Rank",
                        "player": "Player",
                        "franchise": "Franchise",
                        "home_runs": "Runs at Home",
                        "franchise_home_runs": "Franchise Runs at Home",
                        "pct_of_franchise_home_runs": "% of Franchise Home Runs",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    with right:
        st.markdown("### Top 20 Bowlers at Home")
        if bowling.empty:
            st.warning("No eligible home bowling data.")
        else:
            st.dataframe(
                bowling.rename(
                    columns={
                        "rank": "Rank",
                        "player": "Player",
                        "franchise": "Franchise",
                        "home_wickets": "Wickets at Home",
                        "franchise_home_wickets": "Franchise Wickets at Home",
                        "pct_of_franchise_home_wickets": "% of Franchise Home Wickets",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


def render_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning("No phase data available for this scope.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][["rank", "batter", "runs"]]
                .rename(columns={"rank": "Rank", "batter": "Batter", "runs": "Runs"})
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_phase_wicket_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning("No phase-wise wicket data available for this scope.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][["rank", "bowler", "wickets"]]
                .rename(columns={"rank": "Rank", "bowler": "Bowler", "wickets": "Wickets"})
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_batter_impact_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning("No batter impact data available for this scope.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][
                    ["rank", "batter", "runs", "balls", "strike_rate"]
                ]
                .rename(
                    columns={
                        "rank": "Rank",
                        "batter": "Batter",
                        "runs": "Runs",
                        "balls": "Balls",
                        "strike_rate": "Strike Rate",
                    }
                )
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_bowling_impact_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning("No bowling impact data available for this scope.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][
                    ["rank", "bowler", "wickets", "balls", "wicket_per_ball"]
                ]
                .rename(
                    columns={
                        "rank": "Rank",
                        "bowler": "Bowler",
                        "wickets": "Wickets",
                        "balls": "Balls",
                        "wicket_per_ball": "Wickets/Ball",
                    }
                )
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_batter_innings_summary_table(summary_table: pd.DataFrame, title_prefix: str) -> None:
    if summary_table.empty:
        st.warning(f"No eligible batter data for {title_prefix}.")
        return

    display_df = summary_table.rename(
        columns={
            "rank": "Rank",
            "batter": "Batter",
            "innings": "Innings",
            "total_balls": "Total Balls",
            "avg_balls_per_innings": "Avg Balls/Innings",
            "avg_runs_per_innings": "Avg Runs/Innings",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_dot_ball_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning(f"No dot-ball data available for {title_prefix}.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][
                    ["rank", "bowler", "dot_balls", "balls", "dot_ball_pct"]
                ]
                .rename(
                    columns={
                        "rank": "Rank",
                        "bowler": "Bowler",
                        "dot_balls": "Dot Balls",
                        "balls": "Balls",
                        "dot_ball_pct": "Dot Ball %",
                    }
                )
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_boundary_impact_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning(f"No boundary-impact data available for {title_prefix}.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][
                    ["rank", "batter", "boundaries", "balls", "boundary_rate"]
                ]
                .rename(
                    columns={
                        "rank": "Rank",
                        "batter": "Batter",
                        "boundaries": "Boundaries (4s+6s)",
                        "balls": "Balls Faced",
                        "boundary_rate": "Boundaries/Ball",
                    }
                )
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_bowling_avg_phase_tables(phase_table: pd.DataFrame, title_prefix: str) -> None:
    if phase_table.empty:
        st.warning(f"No bowling average data available for {title_prefix}.")
        return

    cols = st.columns(3)
    for col, phase in zip(cols, PHASE_ORDER):
        with col:
            st.markdown(f"### {phase}")
            phase_df = (
                phase_table[phase_table["phase"] == phase][
                    ["rank", "bowler", "runs_conceded", "wickets", "balls", "runs_per_wicket"]
                ]
                .rename(
                    columns={
                        "rank": "Rank",
                        "bowler": "Bowler",
                        "runs_conceded": "Runs Conceded",
                        "wickets": "Wickets",
                        "balls": "Balls",
                        "runs_per_wicket": "Runs/Wicket",
                    }
                )
                .copy()
            )
            if phase_df.empty:
                st.info(f"No records for {phase} in {title_prefix}.")
            else:
                st.dataframe(phase_df, use_container_width=True, hide_index=True)


def render_batter_variance_table(variance_table: pd.DataFrame, title_prefix: str) -> None:
    if variance_table.empty:
        st.warning(f"No eligible batter variance data for {title_prefix}.")
        return

    display_df = variance_table.rename(
        columns={
            "rank": "Rank",
            "batter": "Batter",
            "innings": "Innings",
            "total_runs": "Total Runs",
            "mean_runs": "Avg Runs/Innings",
            "run_variance": "Variance (Runs/Innings)",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_batter_30plus_table(summary_table: pd.DataFrame, title_prefix: str) -> None:
    if summary_table.empty:
        st.warning(f"No eligible 30+ score data for {title_prefix}.")
        return

    display_df = summary_table.rename(
        columns={
            "rank": "Rank",
            "batter": "Batter",
            "total_runs": "Total Runs",
            "innings": "Innings",
            "scores_30_plus": "30+ Innings",
            "pct_30_plus": "% of 30+ Scores",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_bowler_2w_table(summary_table: pd.DataFrame, title_prefix: str) -> None:
    if summary_table.empty:
        st.warning(f"No eligible 2+ wicket innings data for {title_prefix}.")
        return

    display_df = summary_table.rename(
        columns={
            "rank": "Rank",
            "bowler": "Bowler",
            "matches": "Matches",
            "innings_bowled": "Innings Bowled",
            "innings_2plus_wkts": "2+ Wkt Innings",
            "pct_2plus_wkt_innings": "% 2+ Wkt Innings",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_best_batters_by_venue_table(table: pd.DataFrame, title_prefix: str) -> None:
    if table.empty:
        st.warning(f"No eligible venue-batter data for {title_prefix}.")
        return

    display_df = table.rename(
        columns={
            "venue": "Venue",
            "city": "City",
            "rank_in_venue": "Rank in Venue",
            "batter": "Batter",
            "innings": "Innings",
            "runs": "Runs",
            "avg_runs_per_innings": "Avg Runs/Innings",
            "strike_rate": "Strike Rate",
            "balls_per_boundary": "Balls/Boundary",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_venue_and_milestones(
    scoped_df: pd.DataFrame,
    title_prefix: str,
    *,
    trend_reference_df: pd.DataFrame | None = None,
    trend_compare_df: pd.DataFrame | None = None,
    trend_label_first: str | None = None,
    trend_label_second: str | None = None,
) -> None:
    metrics = scope_milestone_summary(scoped_df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("50+ Scores", f"{metrics['50_plus_scores']:,}")
    m2.metric("100+ Scores", f"{metrics['100_plus_scores']:,}")
    m3.metric("2+ Wkt Hauls", f"{metrics['two_plus_wicket_hauls']:,}")
    m4.metric("4+ Wkt Hauls", f"{metrics['four_plus_wicket_hauls']:,}")

    venue_df = venue_innings_averages(scoped_df)
    if venue_df.empty:
        st.warning(f"No venue summary data available for {title_prefix}.")
        return

    if trend_reference_df is not None and trend_label_first and trend_label_second:
        compare_df = scoped_df if trend_compare_df is None else trend_compare_df
        compare_venue_df = venue_innings_averages(compare_df)
        reference_venue_df = venue_innings_averages(trend_reference_df)
        trend_df = _add_venue_score_trend_columns(
            compare_venue_df,
            reference_venue_df,
            first_col_name=trend_label_first,
            second_col_name=trend_label_second,
        )
        venue_df = venue_df.merge(
            trend_df[["venue", "city", trend_label_first, trend_label_second]],
            on=["venue", "city"],
            how="left",
        )

    display_df = venue_df.rename(
        columns={
            "venue": "Venue",
            "city": "City",
            "innings_count_inn1": "1st Innings Samples",
            "avg_total_score_inn1": "Avg 1st Inns Score",
            "avg_boundaries_inn1": "Avg 1st Inns Boundaries",
            "innings_count_inn2": "2nd Innings Samples",
            "avg_total_score_inn2": "Avg 2nd Inns Score",
            "avg_boundaries_inn2": "Avg 2nd Inns Boundaries",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


st.title("IPL Dashboards (2023-2025)")
st.caption("Built from ball-by-ball IPL data.")

with st.sidebar:
    st.header("Data Source")
    data_path = st.text_input("CSV path", value=str(DEFAULT_DATA_PATH))

if not data_path:
    st.warning("Provide a valid CSV path to continue.")
    st.stop()

try:
    raw_df = load_ipl_data(data_path)
except FileNotFoundError:
    st.error(f"File not found: {data_path}")
    st.stop()
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

focus_df = raw_df[raw_df["season"].isin(FOCUS_YEARS)].copy()
available_years = sorted(focus_df["season"].unique().tolist())
missing_years = [year for year in FOCUS_YEARS if year not in available_years]

col1, col2, col3 = st.columns(3)
col1.metric("Years requested", "2023-2025")
col2.metric("Years available", len(available_years))
col3.metric("Rows in scope", f"{len(focus_df):,}")

if missing_years:
    st.info("No records found for: " + ", ".join(map(str, missing_years)))

if focus_df.empty:
    st.warning("No data available in seasons 2023-2025.")
    st.stop()

main_tab, phase_runs_tab, phase_wickets_tab, batter_impact_tab, bowling_impact_tab, batter_summary_tab, dot_ball_tab, boundary_impact_tab, bowling_avg_tab, batter_variance_tab, batter_30plus_tab, bowler_2w_tab, venue_summary_tab, franchise_consistency_tab, best_batters_venue_tab, home_batting_tab, home_bowling_tab, away_batting_tab, away_bowling_tab, batter_home_away_variance_tab, bowler_home_away_variance_tab, nehal_summary_tab, naman_summary_tab, angkrish_summary_tab, ayush_summary_tab, dewald_summary_tab = st.tabs(
    [
        "Runs & Wickets",
        "Phase-wise Runs",
        "Phase-wise Wickets",
        "Batter Impact by Phase",
        "Bowling Impact by Phase",
        "Batter Innings Summary",
        "Dot Ball % by Phase",
        "Boundary Impact by Phase",
        "Runs/Wicket by Phase",
        "Batting Variance",
        "30+ Scores",
        "2+ Wkts %",
        "Venue Summary",
        "Franchise Consistency",
        "Best Batters by Venue",
        "Home Batting Leaders",
        "Home Bowling Leaders",
        "Away Batting Leaders",
        "Away Bowling Leaders",
        "Batter H-A Variance",
        "Bowler H-A Variance",
        "Batter summary - Nehal",
        "Batter summary - Naman",
        "Batter summary - Angkrish",
        "Batter summary - Ayush",
        "Batter summary - Dewald",
    ]
)

with main_tab:
    render_main_leaderboards(focus_df, available_years)

with phase_runs_tab:
    render_phase_leaderboards(focus_df, available_years)

with phase_wickets_tab:
    render_phase_wicket_leaderboards(focus_df, available_years)

with batter_impact_tab:
    render_batter_impact_phase_leaderboards(focus_df, available_years)

with bowling_impact_tab:
    render_bowling_impact_phase_leaderboards(focus_df, available_years)

with batter_summary_tab:
    render_batter_innings_summary(focus_df, available_years)

with dot_ball_tab:
    render_dot_ball_phase_leaderboards(focus_df, available_years)

with boundary_impact_tab:
    render_boundary_impact_phase_leaderboards(focus_df, available_years)

with bowling_avg_tab:
    render_bowling_avg_phase_leaderboards(focus_df, available_years)

with batter_variance_tab:
    render_batter_variance_leaderboards(focus_df, available_years)

with batter_30plus_tab:
    render_batter_30plus_leaderboards(focus_df, available_years)

with bowler_2w_tab:
    render_bowler_2w_leaderboards(focus_df, available_years)

with venue_summary_tab:
    render_venue_summary_tab(focus_df, available_years)

with franchise_consistency_tab:
    render_franchise_squad_consistency_tab(raw_df, available_years)

with best_batters_venue_tab:
    render_best_batters_by_venue_tab(focus_df, available_years)

with home_batting_tab:
    st.subheader("Home Batting Leaders (2023-2025 Combined)")
    st.caption(
        "Top 20 batters by runs at their franchise home grounds. "
        "Includes % contribution vs total franchise home runs."
    )
    batting = home_batting_leaders(focus_df)
    if batting.empty:
        st.warning("No eligible home batting data.")
    else:
        st.dataframe(
            batting.rename(
                columns={
                    "rank": "Rank",
                    "player_display": "Player",
                    "franchise_breakdown": "Franchise Breakdown",
                    "home_runs": "Runs at Home",
                    "franchise_home_runs": "Franchise Runs at Home",
                    "pct_of_franchise_home_runs": "% of Franchise Home Runs",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with home_bowling_tab:
    st.subheader("Home Bowling Leaders (2023-2025 Combined)")
    st.caption(
        "Top 20 bowlers by wickets at their franchise home grounds. "
        "Includes % contribution vs total franchise home wickets."
    )
    bowling = home_bowling_leaders(focus_df)
    if bowling.empty:
        st.warning("No eligible home bowling data.")
    else:
        st.dataframe(
            bowling.rename(
                columns={
                    "rank": "Rank",
                    "player_display": "Player",
                    "franchise_breakdown": "Franchise Breakdown",
                    "home_wickets": "Wickets at Home",
                    "franchise_home_wickets": "Franchise Wickets at Home",
                    "pct_of_franchise_home_wickets": "% of Franchise Home Wickets",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with away_batting_tab:
    st.subheader("Away Batting Leaders (2023-2025 Combined)")
    st.caption(
        "Top 20 batters by runs away from home. "
        "Includes % contribution vs total franchise away runs in seasons/franchises they played."
    )
    away_bat = away_batting_leaders(focus_df)
    if away_bat.empty:
        st.warning("No eligible away batting data.")
    else:
        st.dataframe(
            away_bat.rename(
                columns={
                    "rank": "Rank",
                    "player_display": "Player",
                    "franchise_breakdown": "Franchise Breakdown",
                    "away_runs": "Runs Away",
                    "franchise_away_runs": "Franchise Runs Away",
                    "pct_of_franchise_away_runs": "% of Franchise Away Runs",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with away_bowling_tab:
    st.subheader("Away Bowling Leaders (2023-2025 Combined)")
    st.caption(
        "Top 20 bowlers by wickets away from home. "
        "Includes % contribution vs total franchise away wickets in seasons/franchises they played."
    )
    away_bow = away_bowling_leaders(focus_df)
    if away_bow.empty:
        st.warning("No eligible away bowling data.")
    else:
        st.dataframe(
            away_bow.rename(
                columns={
                    "rank": "Rank",
                    "player_display": "Player",
                    "franchise_breakdown": "Franchise Breakdown",
                    "away_wickets": "Wickets Away",
                    "franchise_away_wickets": "Franchise Wickets Away",
                    "pct_of_franchise_away_wickets": "% of Franchise Away Wickets",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with batter_home_away_variance_tab:
    st.subheader("Batter Home vs Away Variance (2023-2025 Combined)")
    st.caption(
        "Eligibility: minimum 300 runs in each season played during 2023-2025. "
        "Variance metric: |home runs - away runs| / total runs."
    )
    bvar = batter_home_away_variance_summary(focus_df)
    if bvar.empty:
        st.warning("No eligible batter data for variance report.")
    else:
        least = (
            bvar.sort_values(
                ["norm_variance_home_away_runs", "total_runs", "player_display"],
                ascending=[True, False, True],
            )
            .head(TOP_N)
            .reset_index(drop=True)
        )
        least["rank"] = least.index + 1
        most = (
            bvar.sort_values(
                ["norm_variance_home_away_runs", "total_runs", "player_display"],
                ascending=[False, False, True],
            )
            .head(TOP_N)
            .reset_index(drop=True)
        )
        most["rank"] = most.index + 1
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Least Variance (Top 20)")
            st.dataframe(
                least[
                    [
                        "rank",
                        "player_display",
                        "seasons_played",
                        "total_runs",
                        "home_runs",
                        "away_runs",
                        "variance_home_away_runs",
                        "norm_variance_home_away_runs",
                    ]
                ].rename(
                    columns={
                        "rank": "Rank",
                        "player_display": "Player",
                        "seasons_played": "Seasons Played",
                        "total_runs": "Total Runs",
                        "home_runs": "Home Runs",
                        "away_runs": "Away Runs",
                        "variance_home_away_runs": "|Home-Away| Runs",
                        "norm_variance_home_away_runs": "|H-A|/Total Runs",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        with c2:
            st.markdown("### Most Variance (Top 20)")
            st.dataframe(
                most[
                    [
                        "rank",
                        "player_display",
                        "seasons_played",
                        "total_runs",
                        "home_runs",
                        "away_runs",
                        "variance_home_away_runs",
                        "norm_variance_home_away_runs",
                    ]
                ].rename(
                    columns={
                        "rank": "Rank",
                        "player_display": "Player",
                        "seasons_played": "Seasons Played",
                        "total_runs": "Total Runs",
                        "home_runs": "Home Runs",
                        "away_runs": "Away Runs",
                        "variance_home_away_runs": "|Home-Away| Runs",
                        "norm_variance_home_away_runs": "|H-A|/Total Runs",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

with bowler_home_away_variance_tab:
    st.subheader("Bowler Home vs Away Variance (2023-2025 Combined)")
    st.caption(
        "Eligibility: minimum 10 wickets in each season played during 2023-2025. "
        "Variance metric: |home wickets - away wickets| / total wickets."
    )
    wvar = bowler_home_away_variance_summary(focus_df)
    if wvar.empty:
        st.warning("No eligible bowler data for variance report.")
    else:
        least = (
            wvar.sort_values(
                ["norm_variance_home_away_wickets", "total_wickets", "player_display"],
                ascending=[True, False, True],
            )
            .head(TOP_N)
            .reset_index(drop=True)
        )
        least["rank"] = least.index + 1
        most = (
            wvar.sort_values(
                ["norm_variance_home_away_wickets", "total_wickets", "player_display"],
                ascending=[False, False, True],
            )
            .head(TOP_N)
            .reset_index(drop=True)
        )
        most["rank"] = most.index + 1
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Least Variance (Top 20)")
            st.dataframe(
                least[
                    [
                        "rank",
                        "player_display",
                        "seasons_played",
                        "total_wickets",
                        "home_wickets",
                        "away_wickets",
                        "variance_home_away_wickets",
                        "norm_variance_home_away_wickets",
                    ]
                ].rename(
                    columns={
                        "rank": "Rank",
                        "player_display": "Player",
                        "seasons_played": "Seasons Played",
                        "total_wickets": "Total Wickets",
                        "home_wickets": "Home Wickets",
                        "away_wickets": "Away Wickets",
                        "variance_home_away_wickets": "|Home-Away| Wickets",
                        "norm_variance_home_away_wickets": "|H-A|/Total Wkts",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        with c2:
            st.markdown("### Most Variance (Top 20)")
            st.dataframe(
                most[
                    [
                        "rank",
                        "player_display",
                        "seasons_played",
                        "total_wickets",
                        "home_wickets",
                        "away_wickets",
                        "variance_home_away_wickets",
                        "norm_variance_home_away_wickets",
                    ]
                ].rename(
                    columns={
                        "rank": "Rank",
                        "player_display": "Player",
                        "seasons_played": "Seasons Played",
                        "total_wickets": "Total Wickets",
                        "home_wickets": "Home Wickets",
                        "away_wickets": "Away Wickets",
                        "variance_home_away_wickets": "|Home-Away| Wickets",
                        "norm_variance_home_away_wickets": "|H-A|/Total Wkts",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


with nehal_summary_tab:
    render_nehal_batter_summary_tab(focus_df, available_years)


with naman_summary_tab:
    render_naman_batter_summary_tab(focus_df, available_years)


with angkrish_summary_tab:
    render_angkrish_batter_summary_tab(focus_df, available_years)


with ayush_summary_tab:
    render_ayush_batter_summary_tab(focus_df, available_years)


with dewald_summary_tab:
    render_dewald_batter_summary_tab(focus_df, available_years)
