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
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/flow/sd000_20261117_041758` | cube-single-play-singletask-v0 | flow | 0 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | running (app `ap-KjWd1YjHTUPoIUtZwsFgzj`) | Wave 1. FQL reproduction check. |
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/mip/sd000_20261117_041758` | cube-single-play-singletask-v0 | mip | 0 | 1M | same | running (same app) | Wave 1. |
| 2026-11-16 23:18 | `midway/cube-single-play-singletask-v0/regression/sd000_20261117_041759` | cube-single-play-singletask-v0 | regression | 0 | 1M | same | running (same app) | Wave 1. |

## Planned (not launched; needs approval)

| Wave | Group | Envs | Priors | Seeds | Steps | Flags |
|---|---|---|---|---|---|---|
| 1 (launched, see above) | `midway` | cube-single-play-singletask-v0 | flow, mip, regression | 0 | 1M | published alpha (300); `--eval_interval=50000 --save_interval=100000` |
| 2 | `midway` | antmaze-large-navigate-singletask-v0 (alpha=10, q_agg=min), scene-play-singletask-v0 (alpha=300) | flow, mip, regression | 0 | 1M | same |
| 3 | `midway` | all three | flow, mip, regression | 1 | 1M | same |

Launch command (per wave):
```
modal run --detach modal_app.py::batch --envs <env1,env2> --priors flow,mip,regression --seeds <0 or 1> --run-group midway
```
