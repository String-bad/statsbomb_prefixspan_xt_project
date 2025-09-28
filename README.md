# StatsBomb 2018 World Cup — PrefixSpan + xT

This repo provides a fully runnable pipeline to:
1) Download **StatsBomb Open Data** for the 2018 World Cup.
2) Build an **xT (Expected Threat)** grid from event transitions.
3) Tokenize possessions into **action sequences**.
4) Mine **frequent sequential patterns** with **PrefixSpan**.
5) Score patterns by **support / confidence / lift** (for targets: box-entry or shot),
   and by **average ΔxT** of the matched actions.
6) Output CSVs and plots for direct use in your paper.

> No tracking data is needed; only event data.

## Quickstart

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

python -m sbxt.main --output_dir outputs --download 1     --grid_x 12 --grid_y 8 --minsup 0.005 --maxlen 5 --top_k 30
```

Artifacts:
- `outputs/xt_grid.csv` — the xT value per grid cell
- `outputs/patterns.csv` — mined patterns with sup/conf/lift/ΔxT
- `outputs/plots/xt_heatmap.png` — xT heatmap
- `outputs/plots/pattern_*.png` — example path overlays for top patterns
