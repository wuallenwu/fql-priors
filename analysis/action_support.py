"""Action-support analysis on saved fql_prior checkpoints (TA point 4).

At held-out (validation) states, sample K noises and measure, for the prior and the one-step policy:
  spread    std of actions across noises (mean over dims and states)
  dist      L2 distance from each sampled action to the nearest of the actions taken at the k nearest
            training states (obs standardized); `data_dist` is the same for the val action itself
  q         critic value (mean over the two Q heads); `q_data` is Q of the val dataset action
One CSV row per (run, checkpoint step).

    python analysis/action_support.py --runs /vol/exp/fql/midway/scene-play-singletask-v0/*/sd* --out out.csv
"""

import argparse
import csv
import glob
import json
import os

import jax
import jax.numpy as jnp
import ml_collections
import numpy as np

from agents import agents
from envs.env_utils import make_env_and_datasets
from utils.flax_utils import restore_agent

p = argparse.ArgumentParser()
p.add_argument('--runs', nargs='+', required=True, help='run dirs (globs ok), each with flags.json + params_*.pkl')
p.add_argument('--steps', default=','.join(str(s) for s in range(100000, 1000001, 100000)))
p.add_argument('--n_states', type=int, default=512)
p.add_argument('--n_noise', type=int, default=32)
p.add_argument('--k', type=int, default=10)
p.add_argument('--out', required=True)
args = p.parse_args()

runs = sorted(d for pat in args.runs for d in glob.glob(pat))
by_env = {}
for d in runs:
    flags = json.load(open(f'{d}/flags.json'))
    by_env.setdefault(flags['env_name'], []).append((d, flags))


def knn_actions(train, query_obs, k):
    """Actions at the k nearest training states (standardized obs), brute force in chunks."""
    obs = jnp.asarray(train['observations'])
    mu, sd = obs.mean(0), obs.std(0) + 1e-6
    q = (jnp.asarray(query_obs) - mu) / sd
    best_d, best_i = None, None
    for start in range(0, obs.shape[0], 200_000):
        chunk = (obs[start : start + 200_000] - mu) / sd
        d = (q**2).sum(1)[:, None] - 2 * q @ chunk.T + (chunk**2).sum(1)[None]
        neg, idx = jax.lax.top_k(-d, k)
        idx = idx + start
        if best_d is not None:
            neg, j = jax.lax.top_k(jnp.concatenate([best_d, neg], 1), k)
            idx = jnp.take_along_axis(jnp.concatenate([best_i, idx], 1), j, 1)
        best_d, best_i = neg, idx
    return np.asarray(train['actions'])[np.asarray(best_i)]  # (n, k, adim)


def min_dist(acts, nb):
    """acts (..., n, adim), nb (n, k, adim) -> mean over everything of min_k ||a - nb_k||."""
    return float(jnp.sqrt(((acts[..., None, :] - nb) ** 2).sum(-1)).min(-1).mean())


rows = []
for env_name, env_runs in by_env.items():
    _, _, train, val = make_env_and_datasets(env_name)
    rng = np.random.default_rng(0)
    idx = rng.choice(val.size, args.n_states, replace=False)
    obs, a_data = jnp.asarray(val['observations'][idx]), jnp.asarray(val['actions'][idx])
    nb = jnp.asarray(knn_actions(train, obs, args.k))
    data_dist = min_dist(a_data, nb)
    noises = jax.random.normal(jax.random.PRNGKey(0), (args.n_noise, args.n_states, a_data.shape[-1]))

    for d, flags in env_runs:
        config = ml_collections.ConfigDict(flags['agent'])
        agent = agents[config['agent_name']].create(flags['seed'], obs[:1], a_data[:1], config)
        q_fn = lambda a: agent.network.select('critic')(obs, actions=a).mean(0)  # noqa: E731
        for step in args.steps.split(','):
            if not os.path.exists(f'{d}/params_{step}.pkl'):
                continue
            agent = restore_agent(agent, d, step)
            prior_a = jax.vmap(lambda z: agent.compute_flow_actions(obs, noises=z))(noises)
            onestep_a = jnp.clip(jax.vmap(lambda z: agent.network.select('actor_onestep_flow')(obs, z))(noises), -1, 1)
            rows.append(
                dict(
                    env=env_name, prior=config['prior'], alpha=config['alpha'], seed=flags['seed'], step=int(step),
                    prior_spread=float(prior_a.std(0).mean()), onestep_spread=float(onestep_a.std(0).mean()),
                    prior_dist=min_dist(prior_a, nb), onestep_dist=min_dist(onestep_a, nb), data_dist=data_dist,
                    q_prior=float(jax.vmap(q_fn)(prior_a).mean()), q_onestep=float(jax.vmap(q_fn)(onestep_a).mean()),
                    q_data=float(q_fn(a_data).mean()), run=d,
                )
            )  # fmt: skip
            print(rows[-1], flush=True)

os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
with open(args.out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f'wrote {len(rows)} rows to {args.out}')
