import argparse, os, json
import numpy as np
import pandas as pd
from tqdm import tqdm

from .loader import ensure_worldcup_2018
from .xt_model import XTModel
from .sequences import build_possession_sequences
from .prefixspan import prefixspan
from .scoring import score_patterns
from .viz import plot_xt_heatmap, plot_example_path
from .utils import pitch_to_grid


def extract_events(matches, events_by_match):
    events = []
    for m in matches:
        mid = m["match_id"]
        evs = events_by_match[mid]
        for i, e in enumerate(evs):
            e["match_id"] = mid
            if "index" not in e:
                e["index"] = i
            events.append(e)
    return events


def build_xt(events, nx, ny):
    xt = XTModel(nx=nx, ny=ny, gamma=1.0, tol=1e-6, max_iter=500)
    for e in events:
        tname = e.get("type", {}).get("name")
        loc = e.get("location")
        if not loc or len(loc) < 2:
            continue
        x0, y0 = float(loc[0]), float(loc[1])
        xt.add_entry(x0, y0)
        if tname == "Pass":
            p = e.get("pass", {})
            if p.get("outcome") is None:
                end_loc = p.get("end_location")
                if end_loc and len(end_loc) >= 2:
                    x1, y1 = float(end_loc[0]), float(end_loc[1])
                    xt.add_transition(x0, y0, x1, y1)
        elif tname == "Carry":
            c = e.get("carry", {})
            end_loc = c.get("end_location")
            if end_loc and len(end_loc) >= 2:
                x1, y1 = float(end_loc[0]), float(end_loc[1])
                xt.add_transition(x0, y0, x1, y1)
        elif tname == "Shot":
            s = e.get("shot", {})
            xg = float(s.get("statsbomb_xg", 0.0))
            xt.add_shot(x0, y0, xg)
    xt.fit()
    return xt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="open_data_cache", help="Where to cache StatsBomb data")
    ap.add_argument("--output_dir", default="outputs")
    ap.add_argument("--download", type=int, default=1, help="1=download open-data (first run)")
    ap.add_argument("--grid_x", type=int, default=12)
    ap.add_argument("--grid_y", type=int, default=8)
    ap.add_argument("--minsup", type=float, default=0.005, help="min support ratio for PrefixSpan")
    ap.add_argument("--maxlen", type=int, default=5)
    ap.add_argument("--top_k", type=int, default=30)
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    comps, matches, events_by_match = ensure_worldcup_2018(args.data_dir)
    events = extract_events(matches, events_by_match)

    print(f"Loaded {len(matches)} matches, {sum(len(v) for v in events_by_match.values())} events.")

    xt = build_xt(events, args.grid_x, args.grid_y)
    xt_grid = xt.V
    pd.DataFrame(xt_grid).to_csv(os.path.join(args.output_dir, "xt_grid.csv"), index=False)
    plot_xt_heatmap(xt_grid, os.path.join(args.output_dir, "plots/xt_heatmap.png"))

    seqs, grids, used_events = build_possession_sequences(events, (args.grid_x, args.grid_y))
    print(f"Built {len(seqs)} possession sequences.")

    patterns = prefixspan(seqs, minsup_ratio=args.minsup, maxlen=args.maxlen)
    print(f"Mined {len(patterns)} patterns with minsup={args.minsup}.")

    scores = score_patterns(seqs, grids, patterns, xt_grid=np.array(xt_grid))
    df = pd.DataFrame(scores)
    if len(df) == 0:
        print("No patterns met the criteria. Try lowering minsup or increasing maxlen.")
        return

    df_top = df.head(args.top_k)
    out_csv = os.path.join(args.output_dir, "patterns.csv")
    df_top.to_csv(out_csv, index=False)
    print(f"Saved top patterns to {out_csv}")

    os.makedirs(os.path.join(args.output_dir, "plots"), exist_ok=True)
    count = 0
    for _, row in df_top.head(5).iterrows():
        pat = row["pattern"].split()
        for s, g in zip(seqs, grids):
            idxs = []
            i = 0
            for j, tok in enumerate(s):
                if tok == pat[i]:
                    idxs.append(j)
                    i += 1
                    if i == len(pat):
                        break
            if i == len(pat):
                grids_sub = [g[k] for k in idxs]
                tokens_sub = [s[k] for k in idxs]
                save_path = os.path.join(args.output_dir, f"plots/pattern_{count + 1}.png")
                plot_example_path(xt_grid, grids_sub, tokens_sub, save_path, title=row["pattern"])
                count += 1
                break
        if count >= 5:
            break


if __name__ == "__main__":
    main()
