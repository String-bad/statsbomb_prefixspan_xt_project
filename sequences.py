from typing import List, Dict, Any, Tuple
from .utils import pitch_to_grid, token_for_pass, token_for_carry, in_opposition_box


def build_possession_sequences(events: List[Dict[str, Any]], grid_shape=(12, 8)) -> Tuple[
    List[List[str]], List[List[Tuple[int, int]]], List[List[Dict[str, Any]]]]:
    '''
    Returns:
      tokens_per_possession: List of token lists
      grids_per_possession:  List of [(gx,gy) per step], aligned with tokens (for pass/carry steps); for 'SHOT' we append end cell.
      events_per_possession: Original events used for steps (same length as tokens)
    '''
    nx, ny = grid_shape
    possessions = {}
    for ev in events:
        if ev.get("type", {}).get("name") not in ("Pass", "Carry", "Shot", "Dribble"):
            continue
        team = ev.get("team", {}).get("id")
        pid = ev.get("possession")
        mid = ev.get("match_id")
        key = (mid, pid, team)
        possessions.setdefault(key, []).append(ev)

    tokens_all, grids_all, events_all = [], [], []
    for key, evs in possessions.items():
        evs = sorted(evs, key=lambda e: e.get("index", e.get("id", 0)))
        tokens, grids, used = [], [], []
        for e in evs:
            tname = e.get("type", {}).get("name")
            loc = e.get("location")
            if not loc or len(loc) < 2:
                continue
            x0, y0 = float(loc[0]), float(loc[1])

            if tname == "Pass":
                pass_dict = e.get("pass", {})
                end_loc = pass_dict.get("end_location")
                if not end_loc or len(end_loc) < 2:
                    continue
                x1, y1 = float(end_loc[0]), float(end_loc[1])

                if pass_dict.get("outcome") is None:
                    tok = token_for_pass(pass_dict, x0, y0, x1, y1)
                    if in_opposition_box(x1, y1, 1):
                        tok = tok + "_B"
                    tokens.append(tok)
                    grids.append(pitch_to_grid(x0, y0, nx, ny))
                    used.append(e)

            elif tname == "Carry":
                car = e.get("carry", {})
                end_loc = car.get("end_location")
                if not end_loc or len(end_loc) < 2:
                    continue
                x1, y1 = float(end_loc[0]), float(end_loc[1])
                tok = token_for_carry(x0, y0, x1, y1)
                if in_opposition_box(x1, y1, 1):
                    tok = tok + "_B"
                tokens.append(tok)
                grids.append(pitch_to_grid(x0, y0, nx, ny))
                used.append(e)

            elif tname == "Dribble":
                dr = e.get("dribble", {})
                end_loc = dr.get("end_location")
                if end_loc and len(end_loc) >= 2:
                    x1, y1 = float(end_loc[0]), float(end_loc[1])
                    tok = "KSD"
                    if in_opposition_box(x1, y1, 1):
                        tok = tok + "_B"
                    tokens.append(tok)
                    grids.append(pitch_to_grid(x0, y0, nx, ny))
                    used.append(e)

            elif tname == "Shot":
                shot = e.get("shot", {})
                outcome = (shot.get("outcome") or {}).get("name", "")
                if outcome == "Goal":
                    tok = "GOAL"
                else:
                    tok = "SHOT"
                tokens.append(tok)
                grids.append(pitch_to_grid(x0, y0, nx, ny))
                used.append(e)

        if len(tokens) > 0:
            tokens_all.append(tokens)
            grids_all.append(grids)
            events_all.append(used)
    return tokens_all, grids_all, events_all
