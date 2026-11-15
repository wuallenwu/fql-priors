"""Run FQL training on Modal.

Single run:
    modal run modal_app.py --env-name cube-single-play-singletask-v0 \
        --flags "--offline_steps=20000 --eval_interval=10000 --agent.alpha=300"

wandb: set USE_WANDB=1 locally to attach the "wandb" Modal secret (online logging);
otherwise runs log to wandb offline inside /vol/exp.
"""

import os
import shlex
import subprocess

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
    "import os, runpy, sys, wandb; _init = wandb.init; "
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
    try:
        subprocess.run(cmd, cwd=REPO, env=env, check=True)
    finally:
        volume.commit()  # keep partial logs/checkpoints even if the run fails


@app.local_entrypoint()
def main(env_name: str = 'cube-single-play-singletask-v0', seed: int = 0, flags: str = ''):
    train.remote(env_name, seed, shlex.split(flags))
