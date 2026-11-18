"""Alpha sweep: success vs alpha per prior, one panel per env.

    python analysis/plot_alpha.py   # reads results/{alpha,alpha_sweep,midway}/, writes results/alpha/summary.png

Sweep runs live under results/alpha/ (ours) and results/alpha_sweep/ (teammate); the point at the published alpha is
the seed-0 midway run. Score = mean of the last 3 evals (single seed, so read gaps < ~0.1 as noise).
"""

import matplotlib.pyplot as plt
from plot_eval import COLORS, PRIORS, load

PUBLISHED = {'antmaze-large-navigate-singletask-v0': 10, 'scene-play-singletask-v0': 300}


def score(run):
    return sum(s for _, s in run['eval'][-3:]) / 3


def main():
    points = {}  # (env, prior) -> {alpha: score}
    for group in ('alpha', 'alpha_sweep'):
        for (env, prior), runs in load(group).items():
            for r in runs:
                points.setdefault((env, prior), {})[r['alpha']] = score(r)
    for (env, prior), runs in load('midway').items():
        if env in PUBLISHED:  # every prior's published-alpha point, swept or not
            points.setdefault((env, prior), {})[PUBLISHED[env]] = score(next(r for r in runs if r['seed'] == 0))

    envs = [e for e in PUBLISHED if any(k[0] == e for k in points)]
    fig, axes = plt.subplots(1, len(envs), figsize=(4.5 * len(envs), 3.4), sharey=True)
    for ax, env in zip(axes, envs):
        for prior in PRIORS:
            pts = sorted(points.get((env, prior), {}).items())
            if pts:
                ax.plot([a for a, _ in pts], [s for _, s in pts], color=COLORS[prior], marker='o', ms=5, label=prior)
        ax.axvline(PUBLISHED[env], color='gray', ls=':', lw=1)
        ax.text(PUBLISHED[env], 1.0, ' published', color='gray', fontsize=8, va='top')
        ax.set(
            xscale='log', title=env.split('-singletask')[0], xlabel='alpha (distillation weight)', ylim=(-0.02, 1.05)
        )
        ax.grid(alpha=0.25)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(frameon=False, fontsize=8, loc='lower left')
    axes[0].set_ylabel('success (mean of last 3 evals, seed 0)')
    fig.suptitle('Alpha sweep, seed 0: no prior catches the winner at any alpha', fontsize=10)
    fig.tight_layout()
    fig.savefig('results/alpha/summary.png', dpi=150)
    print('wrote results/alpha/summary.png')
    for (env, prior), d in sorted(points.items()):
        print(f'{env[:7]} {prior:10s} ' + '  '.join(f'a{a:g}={s:.2f}' for a, s in sorted(d.items())))


if __name__ == '__main__':
    main()
