# CLAUDE.md — fql-priors (10-703 Deep RL, Fall 2026 final project)

Team: Allen Wu (allenwu), Daniel Guo (dguo3). Two-person team (approved by staff).
Compute: Modal (course gave credits).

## Original proposal (submitted Oct 26)
- Motivation: "Much Ado About Noising" (Pan et al., ICLR 2026; arXiv 2512.01809) found
  that in behavior cloning, a generative policy's success comes from supervised
  iterative computation plus noise injection, not from learning a multimodal
  distribution. Their Minimal Iterative Policy (MIP), a two-step regression-style
  policy, matches flow policies on BC benchmarks.
- Flow Q-Learning (FQL; Park et al., ICML 2025) trains a flow-matching BC policy, then
  trains a separate one-step policy to maximize Q while being distilled toward the flow
  policy's outputs (same noise z in, actions should match). FQL's paper suggests
  modeling multimodal data is part of why it beats Gaussian policies.
- Original idea: replace FQL's flow BC policy with MIP, keep the rest unchanged.
- Original hypothesis: distribution learning matters more in offline RL than in BC,
  because the RL policy is held close to the BC policy. Expected flow to beat MIP on
  more multimodal datasets, and to match it on unimodal ones.
- Proposed milestones: W1 FQL on Modal; W2 MIP as BC policy + dataset multimodality;
  W3 flow vs. MIP comparisons; W4 midway report; W5 analysis + presentation.
- Proposed stretch goals: multimodality dial (datasets with controllable
  multimodality), regression baseline, mode-averaging measurement, wall-clock speed.

## TA feedback (Kshitiz, Nov 3), paraphrased
1. Swapping the flow prior for MIP also changes the targets in FQL's distillation
   objective, so the comparison does NOT isolate distribution learning alone.
2. Frame it as a comparison of behavior priors.
3. Add a regression baseline.
4. Analyze state-conditioned action support to explain performance differences.
5. Much Ado About Noising has relevant component comparisons.

## Our response and decisions
- Reframed question: "How does the choice of behavior prior (flow, MIP, regression)
  inside FQL affect offline RL performance, and what properties of the prior explain
  the differences?" No longer claiming to isolate distribution learning.
- Key technical fact behind the TA's point: the reference MIP sampler is
  deterministic at inference. Step 1 starts from a zero action, and noise is only
  injected during training. So with MIP (or regression) as the prior, FQL's one-step
  policy is distilled toward ONE action per state regardless of z, which is closer
  to TD3+BC-style regularization than to distilling a distribution. We log this
  directly (prior_spread / onestep_spread).
- Regression prior promoted from stretch goal to core arm.
- "Mode averaging" promoted to core, as a state-conditioned action-support analysis:
  at held-out states, sample many actions from each prior and from the one-step
  policy, then measure (a) spread across noise samples, (b) distance to the nearest
  dataset actions at nearby states, (c) Q of sampled vs. dataset actions. Later, also
  at perturbed / less-covered states (Much Ado's Finding 3 is about staying on the
  data manifold for out-of-distribution observations).
- Fairness: matched architecture across priors (same network for all three).
  FQL's alpha (distillation weight) should eventually be tuned per prior, since the
  targets differ in spread. For the midway report, use FQL's published alpha for all
  priors and say so.
- Still stretch goals: multimodality dial, wall-clock speed comparison, MIP with vs.
  without train-time noise inside FQL (Much Ado's component ablation).
- Open: we emailed Kshitiz on Nov 4 asking (1) whether the regression baseline means a
  regression BC prior inside FQL (our assumption) and (2) whether our action-support
  plan matches his intent. No reply yet; proceed with our assumptions.

## Midway report (due Wed Nov 18, 11:59 PM, Gradescope, 2-4 pages, 20 pts)
- Progress & technical work (13 pts): implementation, preliminary experiments with
  plots/tables, key insights/challenges, a takeaways box.
- Datasets/environments/resources (2 pts): include compute usage (GPU hours).
- Updated plan/next steps/risks (5 pts). Also team contributions, reflection.
- Later deadlines: video Dec 1, poster Dec 2/4, final report Dec 8.

## Preliminary experiment plan (midway)
- OGBench, state-based, default task of each env, FQL's published hyperparameters:
  - cube-single-play-singletask-v0 alpha=300 (reproduction check: FQL does well here)
  - scene-play-singletask-v0 alpha=300 (longer-horizon manipulation, play data)
  - antmaze-large-navigate-singletask-v0 alpha=10, q_agg=min (navigation)
- Skip puzzle-3x3 for now (low FQL scores, so gaps are hard to read).
- 3 tasks x 3 priors x 2 seeds = 18 runs at 500k steps (FQL uses 1M),
  eval every 50k.

## Reference code
- FQL (JAX, our base, MIT): https://github.com/seohongpark/fql
  agents/fql.py: actor_loss, compute_flow_actions; network key 'actor_bc_flow'
  (ActorVectorField, inputs obs, action, time); 'actor_onestep_flow'.
- MIP (PyTorch, reference only):
  https://github.com/simchowitzlabpublic/much-ado-about-noising
  mip/losses.py: mip_loss, regression loss; mip/samplers.py: mip_sampler,
  regression_sampler; mip/config.py: t_two_step=0.9, norm_type l2 (squared L2
  summed over action dims).

## Conventions
- agents/fql.py stays untouched so original FQL is always reproducible.
- New code lives in new files where possible; keep diffs to FQL files small.
- Never launch large/expensive Modal jobs without asking.
