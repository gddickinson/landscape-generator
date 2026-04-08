#!/usr/bin/env python3
"""
CLI entry point for terrain generation.

Usage:
    python generate.py                           # defaults
    python generate.py --seed 42 --season winter
    python generate.py --size 256 --output ./out
"""

import argparse
import sys

from terrain.params import EnhancedTerrainParams, Season
from terrain.generator import TerrainGenerator
from terrain.biomes import BiomeColorMapper
from terrain.features import FeatureGenerator
from terrain.visualization import TerrainVisualizer


SEASON_CHOICES = {s.value: s for s in Season}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Procedural landscape generator with biomes, seasons, and features.",
    )
    p.add_argument("--seed", type=int, default=42, help="RNG seed (default: 42)")
    p.add_argument("--size", type=int, default=512, help="Grid size (default: 512)")
    p.add_argument(
        "--season",
        choices=list(SEASON_CHOICES.keys()),
        default="summer",
        help="Season (default: summer)",
    )
    p.add_argument(
        "--density", type=float, default=0.1, help="Feature density (default: 0.1)"
    )
    p.add_argument(
        "--output", type=str, default=".", help="Output directory (default: cwd)"
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    params = EnhancedTerrainParams(
        size=args.size,
        season=SEASON_CHOICES[args.season],
        feature_density=args.density,
    )

    gen = TerrainGenerator(params, seed=args.seed)
    biome_mapper = BiomeColorMapper(params)
    feat_gen = FeatureGenerator(params, gen)
    viz = TerrainVisualizer(params, biome_mapper, output_dir=args.output)

    print(f"Generating terrain (size={args.size}, season={args.season}) ...")

    height_map = gen.generate_fractal_noise()
    moisture_map = gen.generate_fractal_noise()

    height_map, moisture_map = feat_gen.apply_seasonal_effects(height_map, moisture_map)

    feature_masks = {}
    for name, feature in feat_gen.features.items():
        if name == "road_network":
            feature_masks[name] = feat_gen.generate_road_network()
        else:
            feature_masks[name] = feat_gen.generate_feature_mask(feature)

        height_map += feature_masks[name] * feature.height_modifier
        moisture_map += feature_masks[name] * feature.moisture_modifier

    height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min())
    moisture_map = moisture_map.clip(0, 1)

    color_map = viz.generate_color_map(
        height_map, moisture_map, feature_masks, feat_gen.features
    )

    print("Rendering 3D surface ...")
    viz.plot_3d(height_map, color_map)

    print("Rendering analysis views ...")
    viz.plot_analysis(height_map, moisture_map, color_map, feature_masks)

    print("Done.")


if __name__ == "__main__":
    main()
