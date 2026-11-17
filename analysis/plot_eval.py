"""Plot eval success and action spread per prior for every env in a results group.

    python analysis/plot_eval.py midway   # reads results/midway/, writes results/midway/<env>.png, prints a table

Each run dir holds flags.json (env, prior, seed), eval.csv (evaluation/success), train.csv (spreads).
"""

import csv
import json
import os
import sys
from collections import defaultdict

import matplotlib.pyplot as plt

PRIORS = ['flow', 'mip', 'regression']  # fixed order = fixed colors
COLORS = {'flow': '#2a78d6', 'mip': '#eb6834', 'regression': '#1baf7a'}


def read_csv(path, cols):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return [[float(r[c]) for c in cols] for r in rows if all(r.get(c) not in (None, '') for c in cols)]


def load(group):
    runs = defaultdict(list)  # (env, prior) -> list of dict(seed, eval, train)
    for dirpath, _, files in os.walk(f'results/{group}'):
        if 'flags.json' not in files or 'eval.csv' not in files:
            continue
        with open(f'{dirpath}/flags.json') as f:
            flags = json.load(f)
        run = {
            'seed': flags['seed'],
            'eval': read_csv(f'{dirpath}/eval.csv', ['step', 'evaluation/success']),
            'train': read_csv(
                f'{dirpath}/train.csv', ['step', 'training/actor/prior_spread', 'training/actor/onestep_spread']
            )
            if 'train.csv' in files
            else [],
        }
        runs[(flags['env_name'], flags['agent']['prior'])].append(run)
    return runs


def plot_env(env, runs, out):
    fig, (ax_s, ax_sp) = plt.subplots(1, 2, figsize=(10, 3.6))
    for prior in PRIORS:
        rs = runs.get((env, prior), [])
        if not rs:
            continue
        c = COLORS[prior]
        for r in rs:  # individual seeds, faint
            ax_s.plot([s / 1e6 for s, _ in r['eval']], [v for _, v in r['eval']], color=c, alpha=0.25, lw=1)
        steps = [s for s, _ in rs[0]['eval']]
        mean = [
            sum(r['eval'][i][1] for r in rs if i < len(r['eval'])) / sum(1 for r in rs if i < len(r['eval']))
            for i in range(len(steps))
        ]
        ax_s.plot([s / 1e6 for s in steps], mean, color=c, lw=2, marker='o', ms=4, label=f'{prior} (n={len(rs)})')
        if rs[0]['train']:
            t = rs[0]['train']
            ax_sp.plot([s / 1e6 for s, _, _ in t], [p for _, p, _ in t], color=c, lw=2, label=f'{prior} prior')
            ax_sp.plot(
                [s / 1e6 for s, _, _ in t], [o for _, _, o in t], color=c, lw=2, ls='--', label=f'{prior} one-step'
            )
    ax_s.set(title=f'{env}: eval success', xlabel='steps (M)', ylabel='success rate', ylim=(-0.02, 1.02))
    ax_sp.set(title='action spread across noise (seed 0)', xlabel='steps (M)', ylabel='std of actions')
    for ax in (ax_s, ax_sp):
        ax.grid(alpha=0.25)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print('wrote', out)


def table(runs):
    print(f'{"env":40s} {"prior":11s} {"seeds":>5s} {"final":>7s} {"last3":>7s}')
    for (env, prior), rs in sorted(runs.items(), key=lambda kv: (kv[0][0], PRIORS.index(kv[0][1]))):
        final = sum(r['eval'][-1][1] for r in rs) / len(rs)
        last3 = sum(sum(v for _, v in r['eval'][-3:]) / len(r['eval'][-3:]) for r in rs) / len(rs)
        print(f'{env:40s} {prior:11s} {len(rs):5d} {final:7.2f} {last3:7.2f}')


if __name__ == '__main__':
    group = sys.argv[1]
    runs = load(group)
    for env in sorted({env for env, _ in runs}):
        plot_env(env, runs, f'results/{group}/{env}.png')
    table(runs)
