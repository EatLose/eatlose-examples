"""Summarise an EatLose diary. Defaults to the bundled fictional week."""

import argparse
import getpass
import http.client
import json
import os
import re
import sys
from pathlib import Path


def weekly_recap(diary):
    days = diary["nutrition_days"]
    protein = [
        day["estimated_protein_g"] for day in days
        if day["estimated_protein_g"] is not None
    ]
    return {
        "from_date": diary["from_date"],
        "through_date": diary["through_date"],
        "timezone": diary["timezone"],
        "logged_days": len(days),
        "confirmed_meals": sum(day["meal_count"] for day in days),
        "days_with_protein_estimate": len(protein),
        "mean_estimated_protein_g_per_day_with_estimate": (
            round(sum(protein) / len(protein), 1) if protein else None
        ),
    }


def read_authorised_diary():
    token = os.environ.get("EATLOSE_DIARY_TOKEN", "").strip()
    if not token and sys.stdin.isatty():
        token = getpass.getpass("EatLose diary token (hidden): ").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", token):
        raise SystemExit("Use the token after 'Bearer' in the app's copied instruction. "
                         "For unattended use, set EATLOSE_DIARY_TOKEN.")

    connection = http.client.HTTPSConnection("kgnnsvcrxefvavdyvakk.supabase.co", timeout=15)
    try:
        connection.request("GET", "/functions/v1/agent-diary", headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })
        response = connection.getresponse()
        if response.status == 401:
            raise SystemExit("The grant is invalid, expired or disconnected. Check it in EatLose.")
        if response.status == 503:
            raise SystemExit("The diary is temporarily unavailable. Try again later.")
        if response.status != 200:
            raise SystemExit(f"The diary returned HTTP {response.status}.")
        return json.load(response)
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="read the diary you authorised in EatLose")
    args = parser.parse_args()
    try:
        if args.live:
            diary = read_authorised_diary()
        else:
            sample = Path(__file__).with_name("sample-week.json")
            diary = json.loads(sample.read_text(encoding="utf-8"))
        print(json.dumps(weekly_recap(diary), indent=2))
    except (OSError, http.client.HTTPException, UnicodeError, json.JSONDecodeError):
        raise SystemExit("Could not read the diary. Check the file or connection and try again.") from None
