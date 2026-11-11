"""Python reference landscapes for the web Verify page (the browser regenerates the same seeds in JS
and compares). Each result carries the height map and the colour map as palette indices."""
from dataclasses import asdict
from typing import Dict

import numpy as np

from ..params import EnhancedTerrainParams, Season
from ..pipeline import generate_landscape

SEASONS = {s.value: s for s in Season}
CASES = [
    {"name": "summer-seed-42", "seed": 42, "params": {"size": 96, "season": "summer"}},
    {"name": "winter-seed-7", "seed": 7, "params": {"size": 96, "season": "winter", "feature_density": 0.2}},
    {"name": "fall-seed-2024", "seed": 2024, "params": {"size": 64, "season": "fall", "octaves": 4,
                                                        "sea_level": 0.4}},
]
CASE_BY_NAME = {c["name"]: c for c in CASES}
MAX_SIZE = 160


def make_params(raw: Dict) -> EnhancedTerrainParams:
    """EnhancedTerrainParams from a JSON dict (season given by its value, e.g. 'fall')."""
    fields = asdict(EnhancedTerrainParams())
    kw = {k: v for k, v in raw.items() if k in fields}
    if "season" in kw:
        kw["season"] = SEASONS[kw["season"]]
    return EnhancedTerrainParams(**kw)


def run(raw_params: Dict, seed: int) -> Dict:
    """Generate with the Python package; return params, height (12 significant digits) and colours."""
    p = make_params(raw_params)
    if not 16 <= p.size <= MAX_SIZE:
        raise ValueError(f"size must be between 16 and {MAX_SIZE} for a reference run")
    land = generate_landscape(p, seed=seed)
    rgb = np.round(land.color_map * 255).astype(int).reshape(-1, 3)
    hexes = ["#%02X%02X%02X" % tuple(c) for c in rgb]
    palette = sorted(set(hexes))
    pos = {h: i for i, h in enumerate(palette)}
    params = {k: (v.value if isinstance(v, Season) else v) for k, v in asdict(p).items()}
    params["snow_level"] = make_params(raw_params).snow_level  # the requested level, before the season
    return {
        "seed": seed, "params": params, "snow_level": p.snow_level,
        "height": [float("%.12g" % v) for v in land.height_map.ravel()],
        "palette": palette, "colors": "".join(chr(65 + pos[h]) for h in hexes),
    }
