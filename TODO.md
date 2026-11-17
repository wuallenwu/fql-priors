# TODO — midway report due Wed Nov 18, 11:59 PM

Status as of Sun Nov 16: repo = unmodified FQL (verified identical to upstream e8cd16e)
+ Modal entrypoint. No prior code, no runs yet.

## 1. Implementation (Sun)

- [x] `agents/fql_prior.py`: copy of `fql.py` (upstream style); config `prior` in {flow, mip, regression},
      `mip_t=0.9`. Edited `actor_loss` (prior loss, paper Eq. 4.4 for MIP) and `compute_flow_actions`.
      `agents/fql.py` untouched.
      - verify: `prior=flow` gives the same loss as the `fql` agent on the same batch + RNG.
- [x] One loss convention for all priors (FQL style: `jnp.mean` over elements). Noted in module docstring.
- [x] Register `fql_prior` in `agents/__init__.py`.
- [x] Log `prior_spread` and `onestep_spread` (std of actions across noise samples at fixed obs).
      - verify: MIP and regression spread ≈ 0, flow spread > 0.
- [x] Local CPU check (synthetic data, `.venv`): flow == fql on all losses; MIP/regression spread = 0;
      200 updates per prior finite.

## 2. Infrastructure (Sun/Mon)

- [x] `modal_app.py`: batch entrypoint that `train.spawn`s a list of (env, prior, seed) in parallel.
      Single-run path unchanged. Workspace cap is 10 concurrent GPUs (18 runs = ~2 batches, ~3-6 h
      wall-clock total); check nobody else in the workspace is using slots before launching.
- [x] `jax.devices()` printed at the start of every Modal run (smoke run: 78 it/s, cuda plugin installed).
- [x] Modal smoke test: MIP on cube-single, 20k steps: no NaNs, prior_spread = 0, 66% success at 20k,
      2 checkpoints + flags.json on the volume (`exp/fql/smoke/sd000_20261117_040542`).
- [ ] Decide wandb mode for real runs (online via `USE_WANDB=1` makes plotting easier).
- [ ] Add `--save_interval=100000` to every run (default 1M means no checkpoint at 500k steps);
      ~20 MB each, 5 per run, saved to `/vol/exp/...` next to `flags.json`.

## 3. Experiments (Mon → Tue) — ask before launching each wave

- [ ] Wave 1: cube-single, 3 priors, seed 0, 500k steps, `--agent.alpha=300`.
      Flow prior doubles as the FQL reproduction check.
- [ ] Wave 2: antmaze-large-navigate (`--agent.alpha=10 --agent.q_agg=min`) and
      scene-play (`--agent.alpha=300`), 3 priors, seed 0.
- [ ] Wave 3: seed 1 for everything, as soon as wave 1 looks healthy.
- [ ] Record GPU-hours per run from the Modal dashboard.
- [ ] Optional, only if waves 1-3 are launched by Mon morning: cube-single at alpha ∈ {100, 1000}
      for each prior (6 runs), to see whether the prior gap moves with alpha.

## 4. Analysis (Tue)

- [ ] Plot script: eval return vs. step, one line per prior, per env; table of final scores.
- [ ] Spread plot: `prior_spread` / `onestep_spread` over training, per prior.
- [ ] Minimal action-support analysis on cube-single checkpoints: at held-out states, spread of
      sampled actions and k-NN distance to dataset actions at nearby states.
      (Q comparison and perturbed states: after midway.)

## 5. Report (Tue night → Wed)

- [ ] Draft per rubric: progress & technical work with plots, takeaways box, datasets & compute,
      updated plan / risks, team contributions, reflection.
- [ ] Say explicitly: alpha is FQL's published value for every prior, not tuned per prior;
      alpha is not comparable across envs without `normalize_q_loss`.
- [ ] Say explicitly: MIP/regression samplers are deterministic, so the one-step policy is
      distilled toward one action per state (expected, not a bug).
- [ ] Fold in Kshitiz's reply if it arrives; otherwise note the regression-baseline interpretation
      is our assumption.

## Post-midway

- [ ] Per-prior alpha sweep within one env (the clean "how tightly is the policy held" test).
- [ ] More seeds where gaps look real.
- [ ] Action-support analysis: Q of sampled vs. dataset actions; perturbed / low-coverage states.
- [ ] Stretch: multimodality dial dataset; wall-clock comparison; MIP with vs. without noise.

## Housekeeping

- [ ] Commit the uncommitted CLAUDE.md edits.
- [ ] `Archive.zip` at repo root is a snapshot of the repo itself; delete or gitignore it.
