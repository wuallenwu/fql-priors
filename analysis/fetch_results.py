"""Download the small result files (flags.json, train.csv, eval.csv) of every run in a group.

    python analysis/fetch_results.py midway        # -> results/midway/<env>/<prior>/<run>/...

Checkpoints (params_*.pkl) are skipped; fetch those individually with `modal volume get`.
"""

import os
import subprocess
import sys

VOLUME = 'fql-priors'
FILES = ('flags.json', 'train.csv', 'eval.csv')


def ls(path):
    out = subprocess.run(['modal', 'volume', 'ls', VOLUME, path], capture_output=True, text=True, check=True).stdout
    return [line.strip() for line in out.splitlines() if line.strip().startswith(path)]


def fetch_run(remote, local):
    os.makedirs(local, exist_ok=True)
    for f in FILES:  # always re-download: runs in progress keep appending
        r = subprocess.run(
            ['modal', 'volume', 'get', '--force', VOLUME, f'{remote}/{f}', f'{local}/{f}'], check=False, capture_output=True
        )
        print(f'{"ok " if r.returncode == 0 else "missing"} {remote}/{f}')


def walk(remote, local, depth=0):
    entries = ls(remote)
    if any(e.endswith('flags.json') for e in entries):
        fetch_run(remote, local)
    elif depth < 4:
        for e in entries:
            name = e.rsplit('/', 1)[-1]
            walk(e, f'{local}/{name}', depth + 1)


if __name__ == '__main__':
    group = sys.argv[1]
    walk(f'exp/fql/{group}', f'results/{group}')
