import numpy as np
from typing import Dict, Tuple, List
from .utils import pitch_to_grid, cell_id


class XTModel:
    def __init__(self, nx=12, ny=8, gamma=1.0, tol=1e-6, max_iter=500):
        self.nx = nx
        self.ny = ny
        self.N = nx * ny
        self.gamma = gamma
        self.tol = tol
        self.max_iter = max_iter
        self.entries = np.zeros((self.nx, self.ny), dtype=np.float64)
        self.trans = np.zeros((self.N, self.N), dtype=np.float64)
        self.shots = np.zeros((self.nx, self.ny), dtype=np.float64)
        self.shot_xg = np.zeros((self.nx, self.ny), dtype=np.float64)
        self.V = np.zeros((self.nx, self.ny), dtype=np.float64)

    def add_entry(self, x: float, y: float):
        gx, gy = pitch_to_grid(x, y, self.nx, self.ny)
        self.entries[gx, gy] += 1

    def add_transition(self, x0, y0, x1, y1):
        g0 = pitch_to_grid(x0, y0, self.nx, self.ny)
        g1 = pitch_to_grid(x1, y1, self.nx, self.ny)
        i = cell_id(*g0, self.nx)
        j = cell_id(*g1, self.nx)
        self.trans[i, j] += 1

    def add_shot(self, x: float, y: float, xg: float):
        gx, gy = pitch_to_grid(x, y, self.nx, self.ny)
        self.shots[gx, gy] += 1
        self.shot_xg[gx, gy] += xg

    def fit(self):
        entries = self.entries.copy()
        entries[entries == 0] = 1.0

        P_shot = self.shots / entries
        avg_xg = np.zeros_like(self.V)
        nonzero = self.shots > 0
        avg_xg[nonzero] = (self.shot_xg[nonzero] / self.shots[nonzero])

        row_sum = self.trans.sum(axis=1, keepdims=True)
        row_sum[row_sum == 0] = 1.0
        P_move = (self.trans / row_sum).reshape(self.nx, self.ny, self.nx, self.ny)

        V = np.zeros_like(self.V)
        for it in range(self.max_iter):
            V_new = P_shot * avg_xg
            mv = np.einsum("ijxy,xy->ij", P_move, V)
            V_new += self.gamma * mv
            delta = np.max(np.abs(V_new - V))
            V = V_new
            if delta < self.tol:
                break
        self.V = V
        return V

    def value_of(self, x, y):
        gx, gy = pitch_to_grid(x, y, self.nx, self.ny)
        return self.V[gx, gy]
