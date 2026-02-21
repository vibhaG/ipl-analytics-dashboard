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

    batter_col = next((col for col in batter_candidates if col in df.columns), None)
    runs_col = next((col for col in runs_candidates if col in df.columns), None)
    bowler_col = next((col for col in bowler_candidates if col in df.columns), None)
    wicket_kind_col = next((col for col in wicket_kind_candidates if col in df.columns), None)
    over_index_col = next((col for col in over_index_candidates if col in df.columns), None)
    wides_col = next((col for col in wides_candidates if col in df.columns), None)
    noballs_col = next((col for col in noballs_candidates if col in df.columns), None)
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
def top_bowling_impact_by_phase(df: pd.DataFrame) -> pd.DataFrame:
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
    grouped = grouped[grouped["balls"] >= 60].copy()
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
    st.caption("Top 20 bowlers by bowling strike rate: wickets taken / balls bowled")

    scope_tabs = st.tabs([str(y) for y in available_years] + ["2023-2025 Combined"])

    for idx, year in enumerate(available_years):
        with scope_tabs[idx]:
            scoped_df = focus_df[focus_df["season"] == year].copy()
            phase_table = top_bowling_impact_by_phase(scoped_df)
            render_bowling_impact_phase_tables(phase_table, f"Season {year}")

    with scope_tabs[-1]:
        phase_table = top_bowling_impact_by_phase(focus_df)
        render_bowling_impact_phase_tables(phase_table, "Seasons 2023-2025")


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

main_tab, phase_runs_tab, phase_wickets_tab, batter_impact_tab, bowling_impact_tab = st.tabs(
    [
        "Runs & Wickets",
        "Phase-wise Runs",
        "Phase-wise Wickets",
        "Batter Impact by Phase",
        "Bowling Impact by Phase",
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
