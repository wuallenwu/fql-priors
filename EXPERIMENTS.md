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
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/flow/sd001_20261117_070654` | cube-single-play-singletask-v0 | flow | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (54 min) | Wave 3. Final 0.92 (last-3 0.93), peak 1.00. prior_spread 0.06, onestep_spread 0.06. |
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/flow/sd002_20261117_070716` | cube-single-play-singletask-v0 | flow | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (43 min) | Wave 3. Final 0.94 (last-3 0.92), peak 1.00. prior_spread 0.07, onestep_spread 0.06. |
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/mip/sd001_20261117_070720` | cube-single-play-singletask-v0 | mip | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (39 min) | Wave 3. Final 0.90 (last-3 0.87), peak 0.98 at 50k. onestep_spread 0.002. |
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/mip/sd002_20261117_070721` | cube-single-play-singletask-v0 | mip | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (60 min) | Wave 3. Final 0.88 (last-3 0.85), peak 0.98. onestep_spread 0.003. |
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/regression/sd001_20261117_070721` | cube-single-play-singletask-v0 | regression | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (56 min) | Wave 3. Final 0.92 (last-3 0.93), peak 1.00. onestep_spread 0.003. |
| 2026-11-17 02:06 | `midway/cube-single-play-singletask-v0/regression/sd002_20261117_070722` | cube-single-play-singletask-v0 | regression | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (65 min) | Wave 3. Final 0.94 (last-3 0.88), peak 1.00. onestep_spread 0.003. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/flow/sd001_20261117_070723` | antmaze-large-navigate-singletask-v0 | flow | 1 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (89 min) | Wave 3. Final 0.82 (last-3 0.75), peak 0.92. prior_spread 0.15, onestep_spread 0.14. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/flow/sd002_20261117_070721` | antmaze-large-navigate-singletask-v0 | flow | 2 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (57 min) | Wave 3. Final 0.80 (last-3 0.66), peak 0.84. prior_spread 0.15, onestep_spread 0.14. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/mip/sd001_20261117_070723` | antmaze-large-navigate-singletask-v0 | mip | 1 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (45 min) | Wave 3. Final 0.96 (last-3 0.97), peak 1.00. onestep_spread 0.007. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/mip/sd002_20261117_070724` | antmaze-large-navigate-singletask-v0 | mip | 2 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (50 min) | Wave 3. Final 0.78 (last-3 0.79), peak 0.98 at 550k then dropped. onestep_spread 0.007. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/regression/sd001_20261117_074729` | antmaze-large-navigate-singletask-v0 | regression | 1 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (51 min) | Wave 3. Final 0.94 (last-3 0.95), peak 0.98. onestep_spread 0.007. |
| 2026-11-17 02:06 | `midway/antmaze-large-navigate-singletask-v0/regression/sd002_20261117_075228` | antmaze-large-navigate-singletask-v0 | regression | 2 | 1M | `--agent.q_agg=min --agent.alpha=10 --eval_interval=50000 --save_interval=100000` | done (52 min) | Wave 3. Final 0.96 (last-3 0.93), peak 0.98. onestep_spread 0.007. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/flow/sd001_20261117_075740` | scene-play-singletask-v0 | flow | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (65 min) | Wave 3. Final 0.78 (last-3 0.77), peak 0.98. prior_spread 0.06, onestep_spread 0.06. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/flow/sd002_20261117_080200` | scene-play-singletask-v0 | flow | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (83 min) | Wave 3. Final 0.74 (last-3 0.63), peak 0.94 at 300k; noisy. prior_spread 0.06, onestep_spread 0.06. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/mip/sd001_20261117_080241` | scene-play-singletask-v0 | mip | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (68 min) | Wave 3. Final 0.36 (last-3 0.32), peak 0.86 at 300k then declined. onestep_spread 0.003. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/mip/sd002_20261117_080732` | scene-play-singletask-v0 | mip | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (67 min) | Wave 3. Final 0.40 (last-3 0.45), peak 0.82 at 550k then declined. onestep_spread 0.003. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/regression/sd001_20261117_080735` | scene-play-singletask-v0 | regression | 1 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (88 min) | Wave 3. Final 0.32 (last-3 0.33), peak 0.76 at 550k then declined. onestep_spread 0.004. |
| 2026-11-17 02:06 | `midway/scene-play-singletask-v0/regression/sd002_20261117_080739` | scene-play-singletask-v0 | regression | 2 | 1M | `--agent.alpha=300 --eval_interval=50000 --save_interval=100000` | done (81 min) | Wave 3. Final 0.34 (last-3 0.43), peak 0.84 at 100k then declined. onestep_spread 0.004. |
| 2026-11-17 14:41 | `alpha_sweep/a{30,100,1000}/scene-play-singletask-v0/regression`, `alpha_sweep/a{100,1000}/scene-play-singletask-v0/flow` (first attempt) | scene-play-singletask-v0 | regression, flow | 0 | 1M | (broken) | stopped after ~1 min | Launch-loop bug (zsh did not split `"regression 30"`): invalid prior and empty alpha. Apps ap-hutw…, ap-qRLa…, ap-aYXq…, ap-ygCc…, ap-yut4… stopped. Negligible cost. |
| 2026-11-17 14:43 | `alpha_sweep/a30/scene-play-singletask-v0/regression/sd000_20261117_194344` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=30` `--eval_interval=50000 --save_interval=100000` | running | Per-prior alpha sweep (does alpha explain the scene gap?). Published alpha=300 runs are the midway seed-0 runs. flags.json verified. |
| 2026-11-17 14:43 | `alpha_sweep/a100/scene-play-singletask-v0/regression/sd000_20261117_194640` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=100` `--eval_interval=50000 --save_interval=100000` | running | Per-prior alpha sweep (does alpha explain the scene gap?). Published alpha=300 runs are the midway seed-0 runs. flags.json verified. |
| 2026-11-17 14:43 | `alpha_sweep/a1000/scene-play-singletask-v0/regression/sd000_20261117_194832` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=1000` `--eval_interval=50000 --save_interval=100000` | running | Per-prior alpha sweep (does alpha explain the scene gap?). Published alpha=300 runs are the midway seed-0 runs. flags.json verified. |
| 2026-11-17 14:43 | `alpha_sweep/a100/scene-play-singletask-v0/flow/sd000_20261117_194427` | scene-play-singletask-v0 | flow | 0 | 1M | `--agent.alpha=100` `--eval_interval=50000 --save_interval=100000` | running | Per-prior alpha sweep (does alpha explain the scene gap?). Published alpha=300 runs are the midway seed-0 runs. flags.json verified. |
| 2026-11-17 14:43 | `alpha_sweep/a1000/scene-play-singletask-v0/flow/sd000_20261117_194503` | scene-play-singletask-v0 | flow | 0 | 1M | `--agent.alpha=1000` `--eval_interval=50000 --save_interval=100000` | running | Per-prior alpha sweep (does alpha explain the scene gap?). Published alpha=300 runs are the midway seed-0 runs. flags.json verified. |
| 2026-11-17 15:00 | analysis → `/vol/analysis/action_support_<env>.csv` | all 3 midway envs | all | 0,1,2 | (ckpts 100k..1M) | `analysis/action_support.py` defaults: 512 val states, 32 noises, k=10 | done (~15 min, 3 jobs) | 270 rows; CSVs in `results/action_support/`. Scene: MIP/regression one-step actions stay as close to dataset actions as flow's (no off-support drift) while success declines; Q(one-step) - Q(data) shrinks for MIP/regression (1.4 -> 1.0) and stays ~1.25 for flow. |
| 2026-11-17 08:20 | `alpha/antmaze-large-navigate-singletask-v0/flow/alpha3/sd000_<pending>` | antmaze-large-navigate-singletask-v0 | flow | 0 | 1M | `--agent.q_agg=min --agent.alpha=3 --eval_interval=50000 --save_interval=100000` | running (app `ap-apOOUWia8tEOUmncMiXQYV`) | Alpha sweep stage 1 (published alpha=10). |
| 2026-11-17 08:20 | `alpha/antmaze-large-navigate-singletask-v0/flow/alpha30/sd000_<pending>` | antmaze-large-navigate-singletask-v0 | flow | 0 | 1M | `--agent.q_agg=min --agent.alpha=30 --eval_interval=50000 --save_interval=100000` | running (app `ap-apOOUWia8tEOUmncMiXQYV`) | Alpha sweep stage 1 (published alpha=10). |
| 2026-11-17 08:20 | `alpha/antmaze-large-navigate-singletask-v0/flow/alpha100/sd000_<pending>` | antmaze-large-navigate-singletask-v0 | flow | 0 | 1M | `--agent.q_agg=min --agent.alpha=100 --eval_interval=50000 --save_interval=100000` | running (app `ap-apOOUWia8tEOUmncMiXQYV`) | Alpha sweep stage 1 (published alpha=10). |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/mip/alpha100/sd000_<pending>` | scene-play-singletask-v0 | mip | 0 | 1M | `--agent.alpha=100 --eval_interval=50000 --save_interval=100000` | running (app `ap-kkObuG7kuQ8icjzewx2g7g`) | Alpha sweep stage 1 (published alpha=300). Relaunched 16:49 after stopping app `ap-ZpwoAWuFLv1HtHMAzm3Xoj` (its queued regression alpha100/1000 duplicated the `alpha_sweep` rows above); partial dirs from the stopped app deleted. |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/mip/alpha1000/sd000_<pending>` | scene-play-singletask-v0 | mip | 0 | 1M | `--agent.alpha=1000 --eval_interval=50000 --save_interval=100000` | running (app `ap-kkObuG7kuQ8icjzewx2g7g`) | Alpha sweep stage 1 (published alpha=300). Relaunched 16:49 after stopping app `ap-ZpwoAWuFLv1HtHMAzm3Xoj` (its queued regression alpha100/1000 duplicated the `alpha_sweep` rows above); partial dirs from the stopped app deleted. |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/mip/alpha3000/sd000_<pending>` | scene-play-singletask-v0 | mip | 0 | 1M | `--agent.alpha=3000 --eval_interval=50000 --save_interval=100000` | running (app `ap-kkObuG7kuQ8icjzewx2g7g`) | Alpha sweep stage 1 (published alpha=300). Relaunched 16:49 after stopping app `ap-ZpwoAWuFLv1HtHMAzm3Xoj` (its queued regression alpha100/1000 duplicated the `alpha_sweep` rows above); partial dirs from the stopped app deleted. |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/regression/alpha100/sd000_<pending>` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=100 --eval_interval=50000 --save_interval=100000` | cancelled before start | Not run: duplicates the teammate's `alpha_sweep` regression run at this alpha (same seed, same flags); use that row instead. |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/regression/alpha1000/sd000_<pending>` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=1000 --eval_interval=50000 --save_interval=100000` | cancelled before start | Not run: duplicates the teammate's `alpha_sweep` regression run at this alpha (same seed, same flags); use that row instead. |
| 2026-11-17 08:20 | `alpha/scene-play-singletask-v0/regression/alpha3000/sd000_<pending>` | scene-play-singletask-v0 | regression | 0 | 1M | `--agent.alpha=3000 --eval_interval=50000 --save_interval=100000` | running (app `ap-vjBJ5vEHuscF0cFlYHhK2q`) | Alpha sweep stage 1 (published alpha=300). Relaunched 16:49 (see mip rows). |

## Planned (not launched; needs approval)

| Wave | Group | Envs | Priors | Seeds | Steps | Flags |
|---|---|---|---|---|---|---|
| 1 (launched, see above) | `midway` | cube-single-play-singletask-v0 | flow, mip, regression | 0 | 1M | published alpha (300); `--eval_interval=50000 --save_interval=100000` |
| 2 (launched, see above) | `midway` | antmaze-large-navigate-singletask-v0 (alpha=10, q_agg=min), scene-play-singletask-v0 (alpha=300) | flow, mip, regression | 0 | 1M | same |
| 3 (launched, see above) | `midway` | all three envs | flow, mip, regression | 1, 2 | 1M | same |
| alpha stage 1 (launched, see above) | `alpha` | antmaze-large (flow: alpha 3, 30, 100), scene-play (mip, regression: alpha 100, 1000, 3000) | losing arm per env | 0 | 1M | published flags with alpha replaced |
| alpha stage 2 (only if a stage-1 arm reaches the winner's seed range) | `alpha` | same cells | all priors at their best alpha | 0, 1, 2 | 1M | same |

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
| Wave 3 | 18 | 18.6 | wall time from train.csv: cube 39-65 min, antmaze 45-89 min, scene 65-88 min; all 18 finished in ~2 h 5 min wall-clock (app `ap-gWYSASyRHUbY8HuSL7HD4A`) |
| Alpha sweep stage 1 (dguo3) | 7 | ~8.5 (in progress) | 3 antmaze (~55 min), 4 scene (~80 min); regression alpha100/1000 covered by the `alpha_sweep` runs |
| **Total so far** | 37 | **~29 done, ~40 expected** | |
