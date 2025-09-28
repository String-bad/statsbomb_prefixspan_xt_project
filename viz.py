import os
import numpy as np
import matplotlib.pyplot as plt


def plot_xt_heatmap(xt, save_path: str):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.imshow(xt.T, origin="lower", aspect="auto")
    plt.title("xT Heatmap")
    plt.colorbar(label="xT value")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_example_path(xt, grids, tokens, save_path: str, title: str = ""):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.imshow(xt.T, origin="lower", aspect="auto")
    xs = [g[0] for g in grids]
    ys = [g[1] for g in grids]
    plt.plot(xs, ys, marker="o")
    for (x, y), t in zip(grids, tokens):
        plt.text(x, y, t, fontsize=7)
    plt.title(title or "Example sequence over xT")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()
