# CLAUDE.md — fql-priors (10-703 Deep RL, Fall 2026 final project)

Team: Allen Wu (allenwu), Daniel Guo (dguo3). Two-person team (approved by staff).
Compute: Modal (course credits, ~$250/person). Base code: FQL (JAX), MIT license.

## Research question (current framing)

"How does the choice of behavior prior (flow, MIP, regression) inside Flow Q-Learning
affect offline RL performance, and what properties of the prior explain the differences?"

- This is a **comparison of behavior priors**. We do NOT claim to isolate the effect of
  distribution learning: swapping the prior also changes FQL's distillation targets
  (TA feedback, below). Keep this framing in code comments, plots, and any writing.
- Hypothesis carried over from the proposal: distribution learning matters more in
  offline RL than in BC, because the RL policy is held close to the prior. Expect
  flow ≥ MIP ≥ regression on more multimodal datasets, and near-ties on unimodal ones.

## Background

- **Much Ado About Noising** (Pan et al., ICLR 2026; arXiv 2512.01809): in behavior
  cloning, generative policies win because of supervised iterative computation plus
  train-time noise injection, not because they learn a multimodal distribution. Their
  Minimal Iterative Policy (MIP) matches flow on BC benchmarks. They leave RL open.
- **Flow Q-Learning** (FQL; Park et al., ICML 2025): trains a flow-matching BC policy,
  then a separate one-step policy that maximizes Q while being distilled toward the
  flow policy's outputs (same noise z in, actions should match). FQL suggests modeling
  multimodal data is part of why it beats Gaussian policies.
- **Original proposal (Oct 26):** replace FQL's flow BC policy with MIP, keep the rest
  unchanged, compare on datasets with different multimodality.

### TA feedback (Kshitiz, Nov 3), paraphrased
1. Swapping flow for MIP also changes the targets in FQL's distillation objective, so
   the comparison does not isolate distribution learning alone.
2. Frame it as a comparison of behavior priors.
3. Add a regression baseline.
4. Analyze state-conditioned action support to explain performance differences.
5. Much Ado About Noising has relevant component comparisons.

Open: we emailed Kshitiz on Nov 4 asking (1) whether "regression baseline" means a
regression BC prior inside FQL (our assumption) and (2) whether our action-support plan
matches his intent. No reply yet; proceed with our assumptions.

## Experimental design

### Priors (core arms)
All three use the SAME network (`ActorVectorField`: inputs obs, action, time) so
architecture is matched. Only the prior's training loss and sampler differ.

| Prior | Training loss | Sampler at distillation time |
|---|---|---|
| flow (FQL default) | flow matching, t ~ U[0,1] | Euler ODE from noise z, `flow_steps=10` |
| MIP | `‖π(o, 0, t=0) − a‖² + ‖π(o, I_t*, t*) − a‖²`, `I_t* = t*·a + (1−t*)·z`, `t*=0.9` | `a0 = π(o, 0, 0)`, then `a = π(o, t*·a0, t*)` (deterministic) |
| regression | `‖π(o, 0, t=0) − a‖²` | `a = π(o, 0, 0)` (deterministic) |

Key technical fact behind the TA's point: MIP and regression samplers are deterministic.
Noise is only used in MIP's training loss. So with MIP or regression as the prior, the
one-step policy is distilled toward ONE action per state regardless of z, which is
closer to TD3+BC-style regularization than to distilling a distribution. Log this
directly: `prior_spread` and `onestep_spread` (std of actions across z at fixed obs).

Loss-scale note: the MIP reference uses squared L2 summed over action dims; FQL uses
`jnp.mean` over all elements. This only rescales the prior's own loss (the prior gets no
gradient from the distillation term), so it is near-irrelevant under Adam, but pick one
convention, use it for all priors, and say which.

### Action-support analysis (core, per TA point 4)
At held-out states, sample many actions from each prior and from the one-step policy;
measure:
- (a) spread across noise samples,
- (b) distance to the nearest dataset actions at nearby states (k-NN in state space),
- (c) Q of sampled actions vs. Q of dataset actions.
Later: repeat at perturbed / less-covered states (Much Ado's finding about staying on the
data manifold for out-of-distribution observations).

### Fairness
- Matched architecture across priors (above).
- FQL's `alpha` (distillation weight) should eventually be tuned per prior, since the
  targets differ in spread. For the midway report, use FQL's published alpha for all
  priors and say so explicitly.

### Stretch goals (not committed)
Multimodality dial (datasets with controllable multimodality); wall-clock speed
comparison; MIP with vs. without train-time noise inside FQL (Much Ado's component
ablation).

## Deadlines

- **Midway report: Wed Nov 18, 11:59 PM**, Gradescope, 2–4 pages, 20 pts.
  - Progress & technical work (13): implementation, preliminary experiments with
    plots/tables, key insights/challenges, a takeaways box.
  - Datasets/environments/resources (2): include compute usage (GPU hours).
  - Updated plan/next steps/risks (5). Also team contributions, reflection.
- Video Dec 1 · poster Dec 2/4 · final report Dec 8.

### Midway experiment plan
OGBench, state-based, default task of each env, FQL's published hyperparameters:

| env | flags |
|---|---|
| `cube-single-play-singletask-v0` | `--agent.alpha=300` (reproduction check: FQL does well here) |
| `scene-play-singletask-v0` | `--agent.alpha=300` (longer-horizon manipulation, play data) |
| `antmaze-large-navigate-singletask-v0` | `--agent.alpha=10 --agent.q_agg=min` (navigation) |

Skip puzzle-3x3 for now (low FQL scores make gaps hard to read).
3 tasks × 3 priors × 3 seeds = 27 runs at 1M steps (FQL's budget), eval every 50k,
checkpoint every 100k (the `modal_app.py::batch` defaults).

## Repo map and running

- `main.py` — FQL training loop (absl flags; agent config via `--agent.*`).
- `agents/fql.py` — FQL agent. `actor_loss`, `compute_flow_actions`; networks
  `actor_bc_flow` (prior) and `actor_onestep_flow` (deployed policy). **Do not edit.**
- `agents/__init__.py` — agent registry (`agents` dict keyed by `agent_name`).
- `utils/networks.py` — `ActorVectorField`, `Value`.
- `modal_app.py` — Modal entrypoint. A10G GPU, volume `fql-priors` mounted at `/vol`
  (OGBench data cached at `/vol/ogbench`, runs saved to `/vol/exp`).
- `requirements-modal.txt` — pinned deps for Modal (numpy<2, mujoco<4, wandb==0.28.2;
  see comments there for why).
- `agents/fql_prior.py` — copy of `fql.py` with `--agent.prior={flow,mip,regression}`;
  see `diff agents/fql.py agents/fql_prior.py` for the changes.
- `EXPERIMENTS.md` — log of every Modal run (flags, status, result path). Add a row when
  launching, fill in the outcome when it finishes.
- `TODO.md` — task list for the midway report.

Run (smoke test first, always):
```
modal run modal_app.py::main --env-name cube-single-play-singletask-v0 \
    --flags "--offline_steps=20000 --eval_interval=10000 --agent.alpha=300"
```
Batch (parallel, one container per env x prior x seed; `--detach` keeps runs alive after exit):
```
modal run --detach modal_app.py::batch --envs cube-single-play-singletask-v0 \
    --priors flow,mip,regression --seeds 0,1 --run-group midway
```
Alpha sweep: add `--alphas 3,30,100` to replace the env's published alpha; runs then land under
`<group>/<env>/<prior>/alpha<a>/`.
`--run-group` (FQL's `--run_group` flag, default `Debug`) is the wandb group and a directory
level in the save path. Results: `/vol/exp/fql/<group>/<env>/<prior>/sd<seed>_<time>/` for
batch runs, `/vol/exp/fql/<group>/sd<seed>_<time>/` for single runs, each holding
`flags.json`, `train.csv` (incl. `prior_spread`, `onestep_spread`), `eval.csv`, and
`params_<step>.pkl` checkpoints. These CSVs are the record; offline wandb files land in the
container's `/tmp` and are lost. Fetch with `modal volume get fql-priors exp/fql/<path> <local>`.
wandb: set `USE_WANDB=1` locally to attach the `wandb` Modal secret (online logging; the
secret does not exist yet in the `dguo3` workspace). `modal_app.py` currently monkeypatches
`wandb.init` because `main.py` hardcodes `mode='online'` (temporary until `main.py` gets
a `--wandb_mode` flag).

## Reference code

- FQL (JAX, our base): https://github.com/seohongpark/fql
- MIP (PyTorch, reference only — port, don't import):
  https://github.com/simchowitzlabpublic/much-ado-about-noising
  `mip/losses.py`: `mip_loss`, regression loss; `mip/samplers.py`: `mip_sampler`,
  `regression_sampler`; `mip/config.py`: `t_two_step=0.9`, `norm_type` l2.

---

## Working rules

These bias toward caution over speed. For trivial tasks, use judgment.

### Project conventions
- `agents/fql.py` stays untouched so original FQL is always reproducible.
- New code lives in new files where possible; keep diffs to existing FQL files small.
- Match FQL's style: ruff, line length 120, single quotes (`pyproject.toml`).
- **Never launch large or expensive Modal jobs without asking.** A smoke test
  (≤20k steps, one seed) is fine; anything bigger, or any batch of runs, needs a yes.
- Never change a hyperparameter silently. Any deviation from FQL's published settings
  goes in the run's flags and gets mentioned when reporting results.
- **Every Modal run gets a row in `EXPERIMENTS.md`**, smoke tests included. At launch:
  date, result path under `exp/fql/`, env, prior, seeds, steps, flags beyond defaults,
  status (with the Modal app id). When it finishes or is stopped: update status and add
  a one-line outcome (final success, anything odd). Commit the row with the launch.

### 1. Think before coding
- State assumptions explicitly. If uncertain, ask.
- If there are multiple interpretations (e.g., what "spread" or "nearby states" means),
  present them instead of picking one silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop, name what's confusing, and ask.

### 2. Simplicity first
- Minimum code that solves the problem. No features, abstractions, or configurability
  beyond what was asked; no error handling for impossible cases.
- Adding a prior should be a small, readable change, not a framework.
- If 200 lines could be 50, rewrite it. Would a senior engineer call it overcomplicated?

### 3. Surgical changes
- Touch only what the task requires. Don't "improve" adjacent code, comments, or
  formatting, and don't refactor what isn't broken. Match existing style.
- Mention unrelated dead code; don't delete it.
- Remove imports/variables/functions that YOUR change made unused; leave pre-existing
  ones alone.
- Test: every changed line traces directly to the request.

### 4. Goal-driven execution
Turn tasks into verifiable goals and loop until they're met. For multi-step tasks, state
a short plan first:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```
Checks that fit this project:
- New prior → the default `fql` agent's numbers are unchanged, and a 20k-step smoke run
  of the new prior trains without NaNs and logs `prior_spread` / `onestep_spread`.
- MIP / regression sampler → spread across z is ~0 at fixed obs (they're deterministic);
  flow's spread is > 0.
- Reproduction → FQL on cube-single lands near its published score before comparing
  priors against it.
- Modal run → `jax.devices()` shows a GPU, not CPU.

---

These rules are working if diffs contain fewer unnecessary changes, code needs fewer
rewrites for overcomplication, and clarifying questions come before implementation
rather than after mistakes.
