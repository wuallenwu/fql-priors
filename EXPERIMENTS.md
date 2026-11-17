# Experiment log

Every Modal run is recorded here: what was launched, with which flags, and where the results are.
Append a row when launching; fill in status/notes when the run finishes.

## Where results live

Modal volume `fql-priors` (workspace `dguo3`), one directory per run:

```
/vol/exp/fql/<run_group>/sd<seed>_<YYYYMMDD_HHMMSS>/     # ::main runs
/vol/exp/fql/<group>/<env>/<prior>/sd<seed>_<time>/     # ::batch runs
    flags.json      all flags, incl. agent config (prior, alpha, ...)
    train.csv       training metrics every 5k steps (losses, prior_spread, onestep_spread)
    eval.csv        eval metrics every eval_interval (evaluation/success, episode.return)
    params_<step>.pkl   checkpoints every save_interval (~20 MB each)
```

Offline wandb files are written to the container's /tmp and are NOT kept. The CSVs are the record.

List / fetch:
```
modal volume ls fql-priors exp/fql/<path>
modal volume get fql-priors exp/fql/<path>/eval.csv ./local/eval.csv
```

## Runs

| Date (ET) | Group / path under `exp/fql/` | Env | Prior | Seeds | Steps | Flags beyond defaults | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-11-16 23:05 | `smoke/sd000_20261117_040542` | cube-single-play-singletask-v0 | mip | 0 | 20k | `--agent.alpha=300 --eval_interval=10000 --save_interval=10000` | done (4 min) | Smoke test of fql_prior. No NaNs; prior_spread=0; onestep_spread≈0.0035; success 0.66 at 20k. Checkpoints at 10k, 20k. |
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/flow/sd000_20261117_041758` | cube-single-play-singletask-v0 | flow | 0 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (~45 min) | Wave 1. Final success 0.98 (last-3 mean 0.98); FQL reproduces (paper: ~0.9+). prior_spread 0.06, onestep_spread 0.06. |
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/mip/sd000_20261117_041758` | cube-single-play-singletask-v0 | mip | 0 | 1M | same | done (~45 min) | Wave 1. Final 0.96 (last-3 0.96). prior_spread 0, onestep_spread 0.002. |
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/regression/sd000_20261117_041759` | cube-single-play-singletask-v0 | regression | 0 | 1M | same | done (~45 min) | Wave 1. Final 0.98 (last-3 0.93, noisier). prior_spread 0, onestep_spread 0.003. |
| 2026-11-17 00:02 | `midway/antmaze-large-navigate-singletask-v0/flow/sd000_20261117_050225` | antmaze-large-navigate-singletask-v0 | flow | 0 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (52 min) | Wave 2. Final 0.78 (last-3 0.80); noisy, 0.72-0.90 over last 300k. prior_spread 0.14, onestep_spread 0.14. |
| 2026-11-17 00:02 | `midway/antmaze-large-navigate-singletask-v0/mip/sd000_20261117_050227` | antmaze-large-navigate-singletask-v0 | mip | 0 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (74 min) | Wave 2. Final 0.96 (last-3 0.95). prior_spread 0, onestep_spread 0.007. Best on this env. |
| 2026-11-17 00:02 | `midway/antmaze-large-navigate-singletask-v0/regression/sd000_20261117_050225` | antmaze-large-navigate-singletask-v0 | regression | 0 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (45 min) | Wave 2. Final 0.92 (last-3 0.93). prior_spread 0, onestep_spread 0.007. |
| 2026-11-17 00:02 | `midway/scene-play-singletask-v0/flow/sd000_20261117_050227` | scene-play-singletask-v0 | flow | 0 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (99 min) | Wave 2. Final 0.96 (last-3 0.90); noisy (0.64-0.96 over last 400k). prior_spread 0.07, onestep_spread 0.06. |
| 2026-11-17 00:02 | `midway/scene-play-singletask-v0/mip/sd000_20261117_050227` | scene-play-singletask-v0 | mip | 0 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (86 min) | Wave 2. Final 0.62 (last-3 0.51). Peaked 0.84 at 250k then declined. prior_spread 0, onestep_spread 0.003. |
| 2026-11-17 00:02 | `midway/scene-play-singletask-v0/regression/sd000_20261117_050227` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (89 min) | Wave 2. Final 0.64 (last-3 0.56). Peaked 0.90 at 300k then declined. prior_spread 0, onestep_spread 0.004. |

## Planned (not launched; needs approval)

| Wave | Group | Envs | Priors | Seeds | Steps | Flags |
|---|---|---|---|---|---|---|
| 1 (launched, see above) | `midway` | cube-single-play-singletask-v0 | flow, mip, regression | 0 | 1M | published alpha (300); `--eval_interval=50000 --save_interval=100000` |
| 2 (launched, see above) | `midway` | antmaze-large-navigate-singletask-v0 (alpha=10, q_agg=min), scene-play-singletask-v0 (alpha=300) | flow, mip, regression | 0 | 1M | same |
| 3 | `midway` | all three envs | flow, mip, regression | 1, 2 | 1M | same |

Launch command (per wave):
```
modal run --detach modal_app.py::batch --envs <env1,env2> --priors flow,mip,regression --seeds <0 | 1,2> --run-group midway
```

## Compute usage (A10G GPU-hours, estimated from run durations; exact figure: Modal dashboard > Usage)

| Launch | Runs | Approx. GPU-h | Notes |
|---|---|---|---|
| Image build + dataset downloads | - | < 0.5 | one-time per workspace / env |
| Smoke test | 1 | 0.1 | 20k steps, 4 min |
| Wave 1 | 3 | 2.3 | ~45 min per 1M-step run on cube-single |
| Wave 2 | 6 | 7.4 | antmaze 45-74 min, scene-play 86-99 min per 1M-step run (wall time from train.csv) |
| **Total so far** | 10 | **~10** | |
