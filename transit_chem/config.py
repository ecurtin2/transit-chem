from os import getenv
from pathlib import Path

HARMONIC_OSCILLATOR_MAX_N = int(getenv("TRANSIT_HARMONIC_OSCILLATOR_MAX_N", 50))
SMALL_NUMBER = float(getenv("TRANSIT_SMALL_NUMBER", 1e-8))
LARGE_NUMBER = float(getenv("TRANSIT_LARGE_NUMBER", 1000))
FLOAT_TOL = float(getenv("TRANSIT_FLOAT_TOL", 1e-6))
ENABLE_PROGRESSBAR = getenv("TRANSIT_ENABLE_PROGRESSBAR", "False").lower() == "true"


JOBLIB_CACHE_DIR = getenv("TRANSIT_CACHE_DIR", str(Path.home() / ".transit_chem_cache"))
JOBLIB_VERBOSITY = getenv("TRANSIT_JOBLIB_VERBOSITY", 0)
