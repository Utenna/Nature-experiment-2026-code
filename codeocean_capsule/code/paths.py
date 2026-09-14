"""Path shim for the Code Ocean capsule.

Code Ocean mounts data read-only at /data and expects results in /results.
Locally, set CO_DATA / CO_RESULTS to point at the capsule's own folders, e.g.

    export CO_DATA=$(pwd)/../data
    export CO_RESULTS=$(pwd)/../results
"""
import os

_here = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.environ.get("CO_DATA") or (
    "/data" if os.path.isdir("/data") else os.path.join(_here, "..", "data"))
RESULTS_DIR = os.environ.get("CO_RESULTS") or (
    "/results" if os.path.isdir("/results") else os.path.join(_here, "..", "results"))

DATA_DIR = os.path.abspath(DATA_DIR)
RESULTS_DIR = os.path.abspath(RESULTS_DIR)
os.makedirs(RESULTS_DIR, exist_ok=True)


def data(*parts):
    return os.path.join(DATA_DIR, *parts)


def results(*parts):
    return os.path.join(RESULTS_DIR, *parts)
