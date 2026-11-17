"""Bar chart of final success per prior across envs (mean over seeds, with per-seed dots).

    python analysis/plot_summary.py midway   # reads results/midway/, writes results/midway/summary.png

Per-seed score = mean of the last 3 evals (less noisy than the single final eval); bar = mean over seeds,
error bar = std over seeds, dots = individual seeds.
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from plot_eval import COLORS, PRIORS, load

ENV_LABELS = {
    'cube-single-play-singletask-v0': 'cube-single',
    'antmaze-large-navigate-singletask-v0': 'antmaze-large',
    'scene-play-singletask-v0': 'scene-play',
}


def main(group):
    runs = load(group)
    envs = [e for e in ENV_LABELS if any(k[0] == e for k in runs)]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    width = 0.25
    for j, prior in enumerate(PRIORS):
        xs = np.arange(len(envs)) + (j - 1) * width
        for x, env in zip(xs, envs):
            scores = [np.mean([s for _, s in r['eval'][-3:]]) for r in runs.get((env, prior), [])]
            if not scores:
                continue
            ax.bar(x, np.mean(scores), width * 0.9, color=COLORS[prior], label=prior if env == envs[0] else None)
            ax.errorbar(x, np.mean(scores), yerr=np.std(scores), color='black', capsize=3, lw=1)
            ax.scatter(np.full(len(scores), x), scores, color='black', s=10, zorder=3)
            ax.text(x, 1.02, f'{np.mean(scores):.2f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(np.arange(len(envs)))
    ax.set_xticklabels([ENV_LABELS[e] for e in envs])
    ax.set_ylim(0, 1.12)
    ax.set_ylabel('success rate (mean of last 3 evals)')
    ax.set_title('FQL with each behavior prior, 1M steps, 3 seeds (published alpha per env)', fontsize=10)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    out = f'results/{group}/summary.png'
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1])
