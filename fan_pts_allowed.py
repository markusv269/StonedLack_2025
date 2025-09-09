import requests
import pandas as pd
import matplotlib.pyplot as plt

# Liste aller NFL Teams
teams = [
    "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET","GB",
    "HOU","IND","JAX","KC","LV","LAC","LAR","MIA","MIN","NE","NO","NYG","NYJ",
    "PHI","PIT","SF","SEA","TB","TEN","WAS"
]

base_url = "https://api.sleeper.com/stats/nfl/player/{team}?season_type=regular&season=2025&grouping=season"

records = []

for team in teams:
    url = base_url.format(team=team)
    r = requests.get(url)
    data = r.json()
    
    stats = data.get("stats", {})
    fan_pts_allow = {k: v for k, v in stats.items() if k.startswith("fan_pts_allow")}
    
    record = {"team": team}
    record.update(fan_pts_allow)
    records.append(record)

df = pd.DataFrame(records)

# Nur die relevanten Positionen extrahieren
positions = ["fan_pts_allow_qb", "fan_pts_allow_rb", "fan_pts_allow_wr", "fan_pts_allow_te"]
df_plot = df[["team"] + positions].set_index("team")

# Balkendiagramm (gestapelt)
ax = df_plot.plot(kind="bar", stacked=True, figsize=(14, 7))

plt.title("Fantasy Points Allowed per Position (2024 Season)")
plt.xlabel("Team")
plt.ylabel("Fantasy Points Allowed")
plt.xticks(rotation=45)
plt.legend(title="Position")
plt.tight_layout()
plt.show()
print(df_plot.sort_values(by="fan_pts_allow_wr", ascending=False).reset_index())
