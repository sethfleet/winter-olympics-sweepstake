import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL of BBC Sport 2026 Winter Olympics medal table
BBC_MEDAL_URL = "https://www.bbc.co.uk/sport/winter-olympics/italy-2026/medals"

# Mapping from country name (BBC) → IOC code
COUNTRY_TO_IOC = {
    "United States": "USA",
    "Great Britain": "GBR",
    "Norway": "NOR",
    "Germany": "GER",
    "Italy": "ITA",
    "Canada": "CAN",
    "France": "FRA",
    "Sweden": "SWE",
    "Switzerland": "SUI",
    "Netherlands": "NED",
    "Japan": "JPN",
    "China": "CHN",
    "South Korea": "KOR",
    "Czech Republic": "CZE",
    "Austria": "AUT",
    "Slovenia": "SLO",
    "Russia": "RUS",
    "Finland": "FIN",
    "Poland": "POL",
    "Australia": "AUS",
    "Belgium": "BEL",
    "Hungary": "HUN",
    "Spain": "ESP",
    "Latvia": "LAT"
    # add more as needed
}

def fetch_medal_data_bbc():
    """Scrape BBC Sport medal table for 2026 Winter Olympics."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    r = requests.get(BBC_MEDAL_URL, headers=headers, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    medal_table = soup.find("table")
    if not medal_table:
        raise ValueError("Could not find medal table on BBC Sport page")

    medals = {}
    for row in medal_table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
    
        country_td = cols[1]
        raw_text = "".join(country_td.stripped_strings)
    
        # First 3 characters are the IOC code
        ioc = raw_text[:3].upper()
    
        try:
            gold = int(cols[2].get_text(strip=True))
            silver = int(cols[3].get_text(strip=True))
            bronze = int(cols[4].get_text(strip=True))
            total = int(cols[5].get_text(strip=True))
        except ValueError:
            continue
    
        medals[ioc] = {
            "gold": gold,
            "silver": silver,
            "bronze": bronze,
            "total": total
        }

    return medals

def load_participants():
    """Load participants from JSON file. Each participant has 'name' and 'countries' (list of IOC codes)."""
    with open("participants.json") as f:
        return json.load(f)

def compute_scores(participants, medals):
    """Compute each participant's medal totals based on their countries."""
    leaderboard = []
    for p in participants:
        row = {"name": p["name"], "gold":0,"silver":0,"bronze":0,"total":0}
        for c in p["countries"]:
            m = medals.get(c, {"gold":0,"silver":0,"bronze":0,"total":0})
            row["gold"] += m["gold"]
            row["silver"] += m["silver"]
            row["bronze"] += m["bronze"]
            row["total"] += m["total"]
        leaderboard.append(row)

    # Sort by total, then gold, then silver
    leaderboard.sort(key=lambda x: (x["total"], x["gold"], x["silver"]), reverse=True)
    for i, r in enumerate(leaderboard, start=1):
        r["rank"] = i
    return leaderboard

def build_html(leaderboard):
    """Generate index.html leaderboard page."""
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
    medals = fetch_medal_data_bbc()
    participants = load_participants()
    leaderboard = compute_scores(participants, medals)
    build_html(leaderboard)

if __name__ == "__main__":
    main()
