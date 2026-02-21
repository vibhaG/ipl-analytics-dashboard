from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="IPL 2023-2025 Dashboards", layout="wide")

DEFAULT_DATA_PATH = Path("/Users/vibhagopal/Downloads/ipl_data_full.csv")
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


@st.cache_data(show_spinner=False)
def load_ipl_data(data_path: str) -> pd.DataFrame:
    df = pd.read_csv(data_path, low_memory=False)

    batter_candidates = ["striker", "batter"]
    runs_candidates = ["runs_off_bat", "runs_batter"]
    bowler_candidates = ["bowler"]
    wicket_kind_candidates = ["wicket_kind", "wicket_type"]
    over_index_candidates = ["ball_over", "over"]
    wides_candidates = ["extra_wides", "wides"]
    noballs_candidates = ["extra_noballs", "noballs"]
    total_runs_candidates = ["runs_total", "total_runs"]
    extras_candidates = ["extras", "runs_extras"]
    match_id_candidates = ["match_id", "id"]
    innings_candidates = ["innings", "innings_val"]

    batter_col = next((col for col in batter_candidates if col in df.columns), None)
    runs_col = next((col for col in runs_candidates if col in df.columns), None)
    bowler_col = next((col for col in bowler_candidates if col in df.columns), None)
    wicket_kind_col = next((col for col in wicket_kind_candidates if col in df.columns), None)
    over_index_col = next((col for col in over_index_candidates if col in df.columns), None)
    wides_col = next((col for col in wides_candidates if col in df.columns), None)
    noballs_col = next((col for col in noballs_candidates if col in df.columns), None)
    total_runs_col = next((col for col in total_runs_candidates if col in df.columns), None)
    extras_col = next((col for col in extras_candidates if col in df.columns), None)
    match_id_col = next((col for col in match_id_candidates if col in df.columns), None)
    innings_col = next((col for col in innings_candidates if col in df.columns), None)
    ball_col = "ball" if "ball" in df.columns else None

    if "season" not in df.columns or not batter_col or not runs_col or not bowler_col:
        raise ValueError(
            "Could not find required columns. Expected: season + batter + runs + bowler columns."
        )

    keep_cols = ["season", batter_col, runs_col, bowler_col]
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
    if ball_col:
        keep_cols.append(ball_col)

    df = df[keep_cols].copy()

    rename_map = {
        batter_col: "batter",
        runs_col: "runs",
        bowler_col: "bowler",
    }
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

main_tab, phase_runs_tab, phase_wickets_tab, batter_impact_tab, bowling_impact_tab, batter_summary_tab, dot_ball_tab, boundary_impact_tab, bowling_avg_tab, batter_variance_tab, batter_30plus_tab, bowler_2w_tab = st.tabs(
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
