import os, time, json, requests
from typing import List, Dict, Any, Tuple
from tqdm import tqdm

RAW_BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


def _get_json(url, retries=5, sleep=1.0):
    for i in range(retries):
        try:
            r = requests.get(url, headers={"User-Agent": "sbxt/1.0"}, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(sleep * (i + 1))
    raise RuntimeError(f"Failed to GET {url}")


def ensure_worldcup_2018(local_dir: str):
    '''
    Download competitions/matches/events for 2018 FIFA World Cup (comp_id=43, season_id=3).
    Cache to local_dir. Returns (competitions, matches, events_by_match).
    '''
    os.makedirs(local_dir, exist_ok=True)
    comp_path = os.path.join(local_dir, "competitions.json")
    if not os.path.exists(comp_path):
        comps = _get_json(f"{RAW_BASE}/competitions.json")
        with open(comp_path, "w", encoding="utf-8") as f:
            json.dump(comps, f)
    else:
        comps = json.load(open(comp_path, "r", encoding="utf-8"))
    comp_id, season_id = None, None
    for c in comps:
        if str(c.get("competition_name")).lower().startswith("fifa world cup") and str(c.get("season_name")).startswith(
                "2018"):
            comp_id = c["competition_id"]
            season_id = c["season_id"]
            break
    if comp_id is None:
        comp_id, season_id = 43, 3

    matches_path = os.path.join(local_dir, f"matches_{comp_id}_{season_id}.json")
    if not os.path.exists(matches_path):
        matches = _get_json(f"{RAW_BASE}/matches/{comp_id}/{season_id}.json")
        with open(matches_path, "w", encoding="utf-8") as f:
            json.dump(matches, f)
    else:
        matches = json.load(open(matches_path, "r", encoding="utf-8"))

    events_by_match = {}
    ev_dir = os.path.join(local_dir, "events")
    os.makedirs(ev_dir, exist_ok=True)

    for m in tqdm(matches, desc="Downloading events"):
        mid = m["match_id"]
        ep = os.path.join(ev_dir, f"{mid}.json")
        if not os.path.exists(ep):
            ev = _get_json(f"{RAW_BASE}/events/{mid}.json")
            with open(ep, "w", encoding="utf-8") as f:
                json.dump(ev, f)
        else:
            ev = json.load(open(ep, "r", encoding="utf-8"))
        events_by_match[mid] = ev
    return comps, matches, events_by_match
