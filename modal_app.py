"""Run FQL training on Modal.

Single run:
    modal run modal_app.py::main --env-name cube-single-play-singletask-v0 \
        --flags "--offline_steps=20000 --eval_interval=10000 --agent.alpha=300"

Batch (one container per env x prior x seed, in parallel; --detach keeps them alive after this exits):
    modal run --detach modal_app.py::batch --envs cube-single-play-singletask-v0 \
        --priors flow,mip,regression --seeds 0,1 --run-group midway

wandb: set USE_WANDB=1 locally to attach the "wandb" Modal secret (online logging);
otherwise runs log to wandb offline inside /vol/exp.
"""

import os
import shlex
import subprocess
import time

import modal

REPO = '/root/fql'
VOL = '/vol'

image = (
    modal.Image.debian_slim(python_version='3.11')
    .apt_install('libegl1', 'libgl1')
    .pip_install_from_requirements('requirements-modal.txt')
    .env({'MUJOCO_GL': 'egl', 'XLA_PYTHON_CLIENT_PREALLOCATE': 'false'})
    .add_local_dir('.', REPO, ignore=['.git', 'exp', 'wandb', '.venv', '**/__pycache__'])
)
volume = modal.Volume.from_name('fql-priors', create_if_missing=True)
secrets = [modal.Secret.from_name('wandb')] if os.environ.get('USE_WANDB') else []

app = modal.App('fql-priors', image=image)

# main.py hardcodes wandb.init(mode='online'), which beats WANDB_MODE, so force the mode here.
# shortcut: monkeypatch until main.py gets a --wandb_mode flag (commit 4).
SHIM = (
    "import os, runpy, sys, jax, wandb; print('jax devices:', jax.devices(), flush=True); _init = wandb.init; "
    "wandb.init = lambda **k: _init(**{**k, 'mode': os.environ['WANDB_MODE']}); "
    "sys.argv[0] = 'main.py'; runpy.run_path('main.py', run_name='__main__')"
)


@app.function(gpu='A10G', timeout=12 * 3600, volumes={VOL: volume}, secrets=secrets)
def train(env_name: str, seed: int = 0, extra_flags: list[str] = ()):
    # Cache OGBench datasets on the volume (ogbench downloads to ~/.ogbench/data).
    os.makedirs(f'{VOL}/ogbench', exist_ok=True)
    link = os.path.expanduser('~/.ogbench')
    if not os.path.lexists(link):
        os.symlink(f'{VOL}/ogbench', link)

    env = dict(os.environ, WANDB_MODE='online' if os.environ.get('WANDB_API_KEY') else 'offline')
    cmd = ['python', '-c', SHIM, f'--env_name={env_name}', f'--seed={seed}', f'--save_dir={VOL}/exp', *extra_flags]
    print(' '.join(shlex.quote(c) for c in cmd), flush=True)
    proc = subprocess.Popen(cmd, cwd=REPO, env=env)
    try:
        while proc.poll() is None:
            time.sleep(300)
            volume.commit()  # make train.csv / eval.csv / checkpoints visible while the run is in progress
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, cmd)
    finally:
        volume.commit()  # keep partial logs/checkpoints even if the run fails


@app.local_entrypoint()
def main(env_name: str = 'cube-single-play-singletask-v0', seed: int = 0, flags: str = ''):
    train.remote(env_name, seed, shlex.split(flags))


# FQL's published flags per env (github.com/seohongpark/fql README).
PUBLISHED_FLAGS = {
    'cube-single-play-singletask-v0': '--agent.alpha=300',
    'scene-play-singletask-v0': '--agent.alpha=300',
    'antmaze-large-navigate-singletask-v0': '--agent.q_agg=min --agent.alpha=10',
}


@app.local_entrypoint()
def batch(
    envs: str,
    priors: str = 'flow,mip,regression',
    seeds: str = '0',
    run_group: str = 'midway',
    flags: str = '--offline_steps=1000000 --eval_interval=50000 --save_interval=100000',
):
    for env_name in envs.split(','):
        for prior in priors.split(','):
            for seed in seeds.split(','):
                run_flags = [
                    '--agent=agents/fql_prior.py',
                    f'--agent.prior={prior}',
                    f'--run_group={run_group}/{env_name}/{prior}',  # -> /vol/exp/fql/<group>/<env>/<prior>/sd<seed>_<time>/
                    *shlex.split(PUBLISHED_FLAGS[env_name]),
                    *shlex.split(flags),
                ]
                train.spawn(env_name, int(seed), run_flags)
                print(f'spawned {env_name} prior={prior} seed={seed}')


@app.function(gpu='A10G', timeout=2 * 3600, volumes={VOL: volume})
def analyze(script_args: list[str]):
    os.makedirs(f'{VOL}/ogbench', exist_ok=True)
    link = os.path.expanduser('~/.ogbench')
    if not os.path.lexists(link):
        os.symlink(f'{VOL}/ogbench', link)
    try:
        subprocess.run(['python', 'analysis/action_support.py', *script_args], cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=REPO))
    finally:
        volume.commit()


@app.local_entrypoint()
def action_support(args: str):
    """modal run modal_app.py::action_support --args "--runs '/vol/exp/fql/midway/<env>/*/sd*' --out /vol/analysis/x.csv"."""
    analyze.remote(shlex.split(args))
