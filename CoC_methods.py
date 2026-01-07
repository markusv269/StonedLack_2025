import streamlit as st
from sleeper_wrapper import User
import pandas as pd
import requests
from supabase import create_client, Client
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ROUND_NAME = "Wildcard"
# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
@st.cache_data(ttl=6000)
def load_leagues():
    df = pd.DataFrame(
        supabase.table("leagues")
        .select("*")
        .execute()
        .data
    )
    return df[df["league_type"] != "empty"] \
        .sort_values(by=["league_type", "league_sort"]) \
        .reset_index(drop=True)


@st.cache_data(ttl=6000)
def load_managers(batch_size=1000):
    all_rows = []
    start = 0

    while True:
        res = (
            supabase.table("managers")
            .select("league_id, roster_id, display_name")
            .range(start, start + batch_size - 1)
            .execute()
        )

        data = res.data
        if not data:
            break

        all_rows.extend(data)
        start += batch_size

    return pd.DataFrame(all_rows)



@st.cache_data(ttl=6000)
def load_players(player_ids, prices):
    df = pd.DataFrame(
        supabase.table("nfl_players")
        .select("*")
        .in_("player_id", player_ids)
        .execute()
        .data
    )
    df["price"] = df["player_id"].map(prices)
    return df

@st.cache_data(ttl=60)
def load_weekly_player_stats(week: int, prices) -> dict:
    stats = {}  # ← DAS fehlte

    for pid in prices.keys():
        url = (
            f"https://api.sleeper.com/stats/nfl/player/{pid}"
            f"?season_type=post&season=2025&grouping=week"
        )

        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            stats[pid] = 0
            continue

        week_data = r.json().get(str(week))
        if not week_data:
            stats[pid] = 0
            continue

        s = week_data.get("stats", {})
        stats[pid] = (
            s.get("rush_yd", 0) / 10 +
            s.get("rush_td", 0) * 6 +
            s.get("rec_yd", 0) / 10 +
            s.get("rec_td", 0) * 6 +
            s.get("rec", 0) +
            s.get("pass_yd", 0) / 25 +
            s.get("pass_td", 0) * 4 -
            s.get("pass_int", 0) -
            s.get("fum_lost", 0) * 2 +
            s.get("fgm_0_39", 0) * 3 +
            s.get("fgm_40_49", 0) * 4 +
            s.get("fgm_50_plus", 0) * 5 -
            s.get("fgm_missed", 0) +
            s.get("xpm", 0) -
            s.get("xpm_missed", 0)
        )

    return stats


@st.cache_data(ttl=60)
def load_latest_lineups():
    return pd.DataFrame(
        supabase.table("latest_lineups_per_user")
        .select("*")
        .execute()
        .data
    )

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def validate_sleeper_user(username: str) -> str | None:
    try:
        return User(username).get_user_id()
    except Exception:
        return None


def existing_submission(username: str) -> bool:
    res = (
        supabase.table("lineups")
        .select("lineup_id")
        .eq("sleeper_username", username.lower())
        .eq("round", ROUND_NAME)
        .execute()
    )
    return bool(res.data)


def build_player_select(label, df, position, key):
    options = df[df["position"] == position]
    return st.selectbox(
        label,
        options=options["player_id"],
        format_func=lambda pid: (
            f"{options.loc[options.player_id == pid, 'name'].iloc[0]}"
            f" (${options.loc[options.player_id == pid, 'price'].iloc[0]})"
        ),
        key=key
    )
# --------------------------------------------------