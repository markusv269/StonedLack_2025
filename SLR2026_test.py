# app.py
import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

# ----------------------------
# Page config + dark styling
# ----------------------------
st.set_page_config(
    page_title="Click Boss — Week 15 Summary",
    page_icon="📊",
    layout="wide",
)

CUSTOM_CSS = """
<style>
/* App background */
.stApp {
  background: radial-gradient(1200px 600px at 20% 0%, #151a22 0%, #0b0f14 55%, #070a0e 100%);
  color: #e6e9ef;
}

/* Reduce top padding a bit */
.block-container { padding-top: 1.2rem; }

/* Headings */
h1, h2, h3 { letter-spacing: 0.2px; }

/* "Card" */
.cb-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 14px 14px;
  box-shadow: 0 12px 26px rgba(0,0,0,0.35);
}

/* Small label */
.cb-kicker {
  font-size: 0.78rem;
  opacity: 0.75;
  margin-bottom: 6px;
}

/* Divider line */
.cb-divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: 14px 0;
}

/* Matchup layout */
.cb-matchup-title {
  font-weight: 700;
  font-size: 0.98rem;
  margin-bottom: 8px;
  display:flex; align-items:center; gap:8px;
}
.cb-pill {
  display:inline-block;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  opacity: 0.95;
}
.cb-teamrow {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  gap:10px;
  margin: 2px 0;
}
.cb-teamname {
  font-weight: 650;
  font-size: 0.92rem;
}
.cb-score {
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.cb-sub {
  font-size: 0.8rem;
  opacity: 0.85;
  margin-top: 6px;
  line-height: 1.35;
}
.cb-footnote {
  opacity: 0.6;
  font-size: 0.78rem;
  text-align:center;
  margin-top: 10px;
}

/* Make Streamlit widgets fit the theme a bit better */
div[data-testid="stMetricValue"] { color: #e6e9ef; }
div[data-testid="stMetricLabel"] { opacity: 0.75; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------
# Data (mirrors screenshot)
# ----------------------------
BIG_STORY = {
    "intro": (
        "Week 15 in Click Boss (2025) is in the books with strong scoring league-wide "
        "(median: 127.8). The gap between first (166.6) and last (68.6) was massive at 98.0 points."
    ),
    # Each bullet is a ready-to-render HTML line (keeps it flexible)
    "bullets_html": [
        "🏆 <b>Top of the board:</b> <span style='color:#ff6b6b; font-weight:700'>Crashee Rice</span> "
        "posted the week’s highest score at 166.60 points, while "
        "<span style='color:#3ddc84; font-weight:700'>Berns</span> brought up the rear with just 68.60.",

        "🧨 <b>Biggest beatdown:</b> <span style='color:#ff6b6b; font-weight:700'>Krios</span> "
        "vs <span style='color:#ff6b6b; font-weight:700'>Crashee Rice</span> with a margin of 72.44 points.",

        "⚡ <b>Closest game:</b> <span style='color:#ff6b6b; font-weight:700'>Shadowkami</span> "
        "vs <span style='color:#3ddc84; font-weight:700'>Slime Time</span> decided by just 4.04 points.",

        "⭐ <b>Headline performance:</b> <span style='color:#ff6b6b; font-weight:700'>Crashee Rice</span> "
        "– Kyle Pitts Sr. (TE) with 47.60 points.",

        "🛡️ <b>Defensive dominance:</b> <span style='color:#3ddc84; font-weight:700'>Berns</span> "
        "– Eagles D/ST with 16.00 points.",
    ],
}

TOP_PERFORMERS = [
    # (pos, player, pts)
    ("QB", "Trevor Lawrence (JAX)", 58.8),
    ("RB", "Tre'Veyon Henderson (NE)", 40.1),
    ("WR", "Amon-Ra St. Brown (DET)", 43.4),
    ("TE", "Kyle Pitts Sr. (ATL)", 47.6),
    ("K", "Jason Myers (SEA)", 24.0),
    ("RB", "Bo Nix (DEN)", 40.1),
    ("RB", "James Cook III (BUF)", 33.1),
    ("WR", "Puka Nacua (LAR)", 29.9),
    ("WR", "Trey McBride (ARI)", 39.4),
    ("K", "Ka'imi Fairbairn (HOU)", 17.0),
    ("D/ST", "Ravens D/ST (BAL)", 24.0),
    ("D/ST", "Bears D/ST (CHI)", 18.0),
]

MATCHUPS = [
    {
        "left_name": "Shadowkami",
        "left_tag": "HOME · ZEN",
        "left_score": 164.04,
        "right_name": "Slime Time",
        "right_tag": "AWAY · SLIM",
        "right_score": 160.00,
        "badge": "🏆 Championship Bracket · Closest Game",
        "lines": [
            "MVP: James Cook III · 33 pts",
            "🔥 3.90 bench crimes",
            "📈 +36.2 vs league avg",
            "LVP: Will Lutz · 4 pts",
        ],
    },
    {
        "left_name": "Swiftly Chasing Dat Ass",
        "left_tag": "HOME · BCT",
        "left_score": 112.02,
        "right_name": "Cleveland Steamers",
        "right_tag": "AWAY · CS",
        "right_score": 137.88,
        "badge": "🏆 Championship Bracket · Upset",
        "lines": [
            "MVP: Josh Allen · 30 pts",
            "🔥 7.10 bench crimes",
            "📉 -15.8 vs league avg",
            "LVP: Jake Ferguson · 4 pts",
        ],
    },
    {
        "left_name": "Tyreek Deez Nutz",
        "left_tag": "HOME · DET",
        "left_score": 120.40,
        "right_name": "Twisted Wulf",
        "right_tag": "AWAY · KTT",
        "right_score": 135.30,
        "badge": "🪙 Consolation · Striker",
        "lines": [
            "MVP: James Williams · 28 pts",
            "🔥 7.10 bench crimes",
            "📉 -3.5 vs league avg",
            "LVP: Lions D/ST · -5 pts",
        ],
    },
    {
        "left_name": "Jmof",
        "left_tag": "HOME · JM",
        "left_score": 94.22,
        "right_name": "Berns",
        "right_tag": "AWAY · bern",
        "right_score": 68.60,
        "badge": "🪙 Consolation · Striker",
        "lines": [
            "MVP: Jared Goff · 34 pts",
            "🔥 9.80 bench crimes",
            "📉 -33.6 vs league avg",
            "LVP: Titans D/ST · -2 pts",
        ],
    },
    {
        "left_name": "What You Talking ’Bout",
        "left_tag": "HOME · FYTB",
        "left_score": 166.22,
        "right_name": "Burrow The Belt",
        "right_tag": "AWAY · BTB",
        "right_score": 114.98,
        "badge": "🏆 Championship Bracket",
        "lines": [
            "MVP: Amon-Ra St. Brown · 43 pts",
            "🔥 6.50 bench crimes",
            "📈 +38.4 vs league avg",
            "🩹 19.04 proj pts lost (injury)",
        ],
    },
    {
        "left_name": "Krios",
        "left_tag": "HOME · Krio",
        "left_score": 94.16,
        "right_name": "Crashee Rice",
        "right_tag": "AWAY · CR",
        "right_score": 166.60,
        "badge": "🏆 Championship Bracket · Biggest Beatdown",
        "lines": [
            "MVP: Kyle Pitts Sr. · 48 pts",
            "🔥 9.40 bench crimes",
            "📉 -33.7 vs league avg",
            "LVP: Quinton Judkins · 5 pts",
        ],
    },
]

TEAM_SCORES = pd.DataFrame(
    [
        ("Crashee Rice", 166.60),
        ("What You Talking ’Bout", 166.22),
        ("Shadowkami", 164.04),
        ("Slime Time", 160.00),
        ("Cleveland Steamers", 137.88),
        ("Twisted Wulf", 135.30),
        ("Swiftly Chasing Dat Ass", 112.02),
        ("Burrow The Belt", 114.98),
        ("Tyreek Deez Nutz", 120.40),
        ("Krios", 94.16),
        ("Jmof", 94.22),
        ("Berns", 68.60),
    ],
    columns=["Team", "Points"],
)

# metrics (from screenshot)
LEAGUE_MEDIAN = 127.8
LEAGUE_AVG = 127.9
SPREAD = 98.0

# ----------------------------
# Helpers
# ----------------------------
def render_card_start():
    st.markdown('<div class="cb-card">', unsafe_allow_html=True)

def render_card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def matchup_card(m):
    render_card_start()
    st.markdown(
        f'<div class="cb-matchup-title">⚔️ {m["left_name"]} <span style="opacity:.55">vs</span> {m["right_name"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="cb-kicker"><span class="cb-pill">{m["badge"]}</span></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="cb-teamrow">
          <div>
            <div class="cb-teamname">{m["left_tag"]}</div>
          </div>
          <div class="cb-score">{m["left_score"]:.2f} pts</div>
        </div>
        <div class="cb-teamrow" style="margin-top:4px;">
          <div>
            <div class="cb-teamname">{m["right_tag"]}</div>
          </div>
          <div class="cb-score">{m["right_score"]:.2f} pts</div>
        </div>
        <div class="cb-divider"></div>
        <div class="cb-sub">
          {"<br/>".join(m["lines"])}
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_card_end()

def top_performers_table(items):
    df = pd.DataFrame(items, columns=["Pos", "Player", "Pts"])
    df["Pts"] = df["Pts"].map(lambda x: f"{x:.1f}")
    render_card_start()
    st.markdown("### Top Performers")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pos": st.column_config.TextColumn(width="small"),
            "Player": st.column_config.TextColumn(width="large"),
            "Pts": st.column_config.TextColumn(width="small"),
        },
    )
    render_card_end()

def big_story_card(story):
    render_card_start()
    st.markdown("### Big Story")
    st.write(story["intro"])
    for line in story.get("bullets_html", []):
        st.markdown(line, unsafe_allow_html=True)
    render_card_end()

def scoring_distribution_chart(df_scores: pd.DataFrame):
    # preserve "bar rainbow" feel by assigning a category (Altair will color by default)
    chart_df = df_scores.copy()
    chart_df["Team"] = pd.Categorical(chart_df["Team"], categories=chart_df.sort_values("Points", ascending=False)["Team"])
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Team:N", sort="-y", axis=alt.Axis(labelAngle=-35, title=None)),
            y=alt.Y("Points:Q", title=None),
            color=alt.Color("Team:N", legend=None),
            tooltip=["Team:N", alt.Tooltip("Points:Q", format=".2f")],
        )
        .properties(height=230)
    )

    median_rule = alt.Chart(pd.DataFrame({"y": [LEAGUE_MEDIAN]})).mark_rule(strokeDash=[6, 6]).encode(y="y:Q")
    return chart + median_rule

# ----------------------------
# Header
# ----------------------------
left, right = st.columns([0.72, 0.28], vertical_alignment="center")
with left:
    st.title("📊 Click Boss — Week 15 Summary")

with right:
    # Minimal CSV to match the "Download CSV" feel
    csv_buf = StringIO()
    TEAM_SCORES.to_csv(csv_buf, index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="week15_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("")

# ----------------------------
# Top area: Big story + Top performers
# ----------------------------
col_story, col_perf = st.columns([0.62, 0.38], gap="large")
with col_story:
    big_story_card(BIG_STORY)
with col_perf:
    top_performers_table(TOP_PERFORMERS)

st.markdown("")
st.markdown('<div class="cb-divider"></div>', unsafe_allow_html=True)

# ----------------------------
# Tabs (like the screenshot row)
# ----------------------------
tabs = st.tabs(["Summary", "Stats", "DET vs KTT", "Matchups", "Best / Worst", "Standings", "How to CR"])

# We replicate screenshot focus: Matchups + League Shape on "Summary"
with tabs[0]:
    st.markdown("## 🧩 Matchups")

    # 2-column grid, 3 rows (6 matchup cards)
    grid_cols = st.columns(2, gap="large")
    for i, m in enumerate(MATCHUPS):
        with grid_cols[i % 2]:
            matchup_card(m)

    st.markdown("")
    st.markdown("## 📈 League Shape")

    # Little “toggle” feel (non-functional, just UI-ish)
    toggle_cols = st.columns([0.22, 0.22, 0.22, 0.34])
    toggle_cols[0].markdown("🔴 **Scoring Distribution**")
    toggle_cols[1].markdown("🟢 Projected vs Actual")
    toggle_cols[2].markdown("🟡 Luck & Schedule")
    toggle_cols[3].markdown("")

    render_card_start()
    st.markdown("**Scoring Distribution**")
    st.altair_chart(scoring_distribution_chart(TEAM_SCORES), use_container_width=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("League Median", f"{LEAGUE_MEDIAN:.1f} pts")
    with m2:
        st.metric("League Average", f"{LEAGUE_AVG:.1f} pts")
    with m3:
        st.metric("Spread", f"{SPREAD:.1f} pts")

    with st.expander("All Facts (Advanced)"):
        st.dataframe(TEAM_SCORES.sort_values("Points", ascending=False), use_container_width=True, hide_index=True)

    render_card_end()

    st.markdown('<div class="cb-footnote">Data through Week 15</div>', unsafe_allow_html=True)

# Fill other tabs with light placeholders (so the UI matches the screenshot’s tab row)
with tabs[1]:
    st.info("Stats tab placeholder — add your deeper breakdowns here (player totals, positions, efficiency, etc.).")

with tabs[2]:
    st.info("DET vs KTT placeholder — add a head-to-head focused view here.")

with tabs[3]:
    st.info("Matchups placeholder — you can move the matchup grid here if you want tabs to be functional.")

with tabs[4]:
    st.info("Best / Worst placeholder — add weekly highs/lows, bench crimes, luck index, etc.")

with tabs[5]:
    st.info("Standings placeholder — add current standings, playoff picture, clinch scenarios.")

with tabs[6]:
    st.info("How to CR placeholder — add explainer content for your custom metrics.")
