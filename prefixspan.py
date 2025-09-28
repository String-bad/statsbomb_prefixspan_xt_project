from typing import List, Dict, Any, Tuple
from collections import defaultdict


def _project_db(seqs: List[List[str]], occs: List[int], prefix: List[str]):
    if not prefix:
        return list(range(len(seqs))), [0] * len(seqs)

    last = prefix[-1]
    proj_ids, proj_pos = [], []
    for i, seq in enumerate(seqs):
        start = occs[i]
        j = start
        while j < len(seq):
            if seq[j] == last:
                proj_ids.append(i)
                proj_pos.append(j + 1)
                break
            j += 1
    return proj_ids, proj_pos


def _freq_items(seqs: List[List[str]], ids: List[int], pos: List[int], minsup: int):
    counts = defaultdict(int)
    for idx, p in zip(ids, pos):
        s = seqs[idx]
        used = set()
        for j in range(p, len(s)):
            it = s[j]
            if it not in used:
                counts[it] += 1
                used.add(it)
    return [(it, c) for it, c in counts.items() if c >= minsup]


def prefixspan(seqs: List[List[str]], minsup_ratio: float, maxlen: int = 5):
    N = len(seqs)
    minsup = max(1, int(minsup_ratio * N + 1e-9))
    results = []

    def _grow(prefix: List[str], ids: List[int], pos: List[int]):
        if len(prefix) > 0:
            results.append((prefix[:], len(ids)))
        if len(prefix) >= maxlen:
            return
        freq = _freq_items(seqs, ids, pos, minsup)
        freq.sort(key=lambda x: (-x[1], x[0]))
        for it, sup in freq:
            ids2, pos2 = _project_db([seqs[i] for i in ids], pos, [it])
            real_ids = [ids[k] for k in ids2]
            _grow(prefix + [it], real_ids, pos2)

    ids0 = list(range(N))
    pos0 = [0] * N
    _grow([], ids0, pos0)
    uniq = {}
    for p, s in results:
        t = tuple(p)
        if t not in uniq or s > uniq[t]:
            uniq[t] = s
    return [(list(k), v) for k, v in sorted(uniq.items(), key=lambda x: (-x[1], x[0]))]
