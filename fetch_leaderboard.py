import json
import requests
from datetime import datetime

MEDALS_URL = "https://apis.codante.io/olympic-games/countries"


def fetch_medal_data():
    r = requests.get(MEDALS_URL)
    r.raise_for_status()
    res = r.json()

    lookup = {}
    for c in res.get("data", []):
        code = c.get("id")
        lookup[code] = {
            "gold": c.get("gold_medals", 0),
            "silver": c.get("silver_medals", 0),
            "bronze": c.get("bronze_medals", 0),
            "total": c.get("total_medals", 0)
        }
    return lookup


def load_participants():
    with open("participants.json") as f:
        return json.load(f)


def compute_scores(participants, medals):
    board = []

    for p in participants:
        row = {
            "name": p["name"],
            "gold": 0,
            "silver": 0,
            "bronze": 0,
            "total": 0,
        }

        for c in p["countries"]:
            m = medals.get(c, {"gold":0,"silver":0,"bronze":0,"total":0})
            row["gold"] += m["gold"]
            row["silver"] += m["silver"]
            row["bronze"] += m["bronze"]
            row["total"] += m["total"]

        board.append(row)

    board.sort(key=lambda x: (x["total"], x["gold"], x["silver"]), reverse=True)

    for i, r in enumerate(board, start=1):
        r["rank"] = i

    return board


def build_html(leaderboard):
    updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    rows = ""
    for r in leaderboard:
        rows += f"""
        <tr>
          <td>{r['rank']}</td>
          <td>{r['name']}</td>
          <td>{r['gold']}</td>
          <td>{r['silver']}</td>
          <td>{r['bronze']}</td>
          <td><b>{r['total']}</b></td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Olympics Sweepstake Leaderboard</title>
        <meta http-equiv="refresh" content="300">
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            table {{ border-collapse: collapse; }}
            th, td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; }}
            th {{ background: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>🏅 Leaderboard</h1>
        <p>Last updated: {updated}</p>

        <table>
            <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Gold</th>
                <th>Silver</th>
                <th>Bronze</th>
                <th>Total</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    with open("index.html", "w") as f:
        f.write(html)


def main():
    medals = fetch_medal_data()
    participants = load_participants()
    leaderboard = compute_scores(participants, medals)
    build_html(leaderboard)


if __name__ == "__main__":
    main()
