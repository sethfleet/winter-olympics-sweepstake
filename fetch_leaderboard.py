import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright

# Official 2026 Winter Olympics medal table
URL = "https://www.olympics.com/en/milano-cortina-2026/medals"

def fetch_medal_data():
    """
    Uses Playwright to render the page and extract current 2026 medals.
    Returns a dictionary of {country_code: {"gold":.., "silver":.., "bronze":.., "total":..}}
    """
    medals = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # wait 5 seconds for table to load

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Adjust selector if needed; this usually finds the table rows
    rows = soup.find_all("tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
        country_code = cols[1].text.strip()
        try:
            gold = int(cols[2].text.strip())
            silver = int(cols[3].text.strip())
            bronze = int(cols[4].text.strip())
            total = int(cols[5].text.strip())
        except ValueError:
            continue

        medals[country_code] = {
            "gold": gold,
            "silver": silver,
            "bronze": bronze,
            "total": total
        }

    return medals

def load_participants():
    with open("participants.json") as f:
        return json.load(f)

def compute_scores(participants, medals):
    board = []
    for p in participants:
        row = {"name": p["name"], "gold":0,"silver":0,"bronze":0,"total":0}
        for c in p["countries"]:
            m = medals.get(c, {"gold":0,"silver":0,"bronze":0,"total":0})
            row["gold"] += m["gold"]
            row["silver"] += m["silver"]
            row["bronze"] += m["bronze"]
            row["total"] += m["total"]
        board.append(row)

    # Rank: total first, then gold, then silver
    board.sort(key=lambda x: (x["total"], x["gold"], x["silver"]), reverse=True)
    for i, r in enumerate(board, start=1):
        r["rank"] = i
    return board

def build_html(leaderboard):
    updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    rows_html = ""
    for r in leaderboard:
        rows_html += f"""
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
        <title>2026 Winter Olympics Sweepstake</title>
        <meta http-equiv="refresh" content="300">
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; }}
            th {{ background: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>🏅 2026 Winter Olympics Leaderboard</h1>
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
            {rows_html}
        </table>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    medals = fetch_medal_data()
    participants = load_participants()
    leaderboard = compute_scores(participants, medals)
    build_html(leaderboard)

if __name__ == "__main__":
    main()
