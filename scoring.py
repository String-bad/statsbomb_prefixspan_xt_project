from typing import List, Tuple, Dict, Any
import numpy as np


def contains_subseq(seq: List[str], pat: List[str]) -> bool:
    i = 0
    for tok in seq:
        if tok == pat[i]:
            i += 1
            if i == len(pat):
                return True
    return False


def index_of_subseq(seq: List[str], pat: List[str]):
    i = 0
    for j, tok in enumerate(seq):
        if tok == pat[i]:
            i += 1
            if i == len(pat):
                return j
    return -1


def score_patterns(seqs: List[List[str]], grids: List[List[tuple]], patterns: List[Tuple[List[str], int]],
                   xt_grid: np.ndarray):
    N = len(seqs)
    target_any = [(("SHOT" in s) or ("GOAL" in s) or any(tok.endswith("_B") for tok in s)) for s in seqs]
    P_target = sum(target_any) / N if N > 0 else 0.0

    out = []
    for pat, sup_count in patterns:
        if len(pat) < 2:
            continue
        last = pat[-1]
        is_target = (last in ("SHOT", "GOAL")) or last.endswith("_B")
        if not is_target:
            continue
        antecedent = pat[:-1]
        seq_has_ant = []
        seq_has_both = []
        dxt_values = []

        for s, g in zip(seqs, grids):
            has_ant = contains_subseq(s, antecedent)
            if not has_ant:
                continue
            seq_has_ant.append(1)
            end_idx = index_of_subseq(s, antecedent)
            has_target_after = False
            for j in range(end_idx + 1, len(s)):
                tok = s[j]
                if last in ("SHOT", "GOAL"):
                    if tok in ("SHOT", "GOAL"):
                        has_target_after = True
                        dxt = 0.0
                        for k in range(end_idx, j):
                            g_curr = g[k]
                            g_next = g[k + 1] if k + 1 < len(g) else g[k]
                            val_curr = xt_grid[g_curr[0], g_curr[1]]
                            val_next = xt_grid[g_next[0], g_next[1]]
                            dxt += (val_next - val_curr)
                        dxt_values.append(dxt)
                        break
                else:
                    if tok.endswith("_B"):
                        has_target_after = True
                        k = j - 1 if j - 1 >= 0 else j
                        g_curr = g[k]
                        g_next = g[k + 1] if k + 1 < len(g) else g[k]
                        val_curr = xt_grid[g_curr[0], g_curr[1]]
                        val_next = xt_grid[g_next[0], g_next[1]]
                        dxt_values.append(val_next - val_curr)
                        break
            if has_target_after:
                seq_has_both.append(1)

        sup_ant = sum(seq_has_ant)
        sup_both = sum(seq_has_both)
        if sup_ant == 0:
            continue
        conf = sup_both / sup_ant
        lift = (conf / P_target) if P_target > 0 else 0.0
        support_ratio = sup_both / N
        avg_dxt = float(np.mean(dxt_values)) if len(dxt_values) > 0 else 0.0

        out.append({
            "pattern": " ".join(pat),
            "length": len(pat),
            "support": support_ratio,
            "support_count": sup_both,
            "antecedent_count": sup_ant,
            "confidence": conf,
            "lift": lift,
            "avg_dxt": avg_dxt,
            "target": "SHOT" if last in ("SHOT", "GOAL") else "BOX"
        })
    out.sort(key=lambda x: (-x["lift"], -x["confidence"], -x["support"], -x["avg_dxt"]))
    return out
