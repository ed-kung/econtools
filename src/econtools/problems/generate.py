"""
Generate, save, and load the set of valid parameterizations for problem types.

For a problem class `cls`, the valid set is every dict yielded by
`cls.candidate_params(rng)` whose built problem passes `check_solution()`.
Each valid problem contributes one row, `problem.record()` (= params | sol),
to <data_dir>/<ClassName>.csv (or .pkl, per `cls.data_format`).
"""

import argparse
import os

import numpy as np
import pandas as pd

from econtools.problems import base


class NoValidProblemsError(RuntimeError):
    pass


def data_path(cls, data_dir=None):
    data_dir = data_dir if data_dir is not None else base.config.data_dir
    return os.path.join(data_dir, f"{cls.__name__}.{cls.data_format}")


def generate(cls, rng=None, verbose=False):
    """Build every candidate and return a DataFrame of the valid ones."""
    if rng is None:
        rng = np.random.default_rng(cls.seed)
    rows = []
    n_tried = 0
    for params in cls.candidate_params(rng):
        n_tried += 1
        problem = cls(params=params, rng=rng)
        if problem.check_solution():
            rows.append(problem.record())
    df = pd.DataFrame.from_records(rows)
    if len(df) > 0 and cls.data_format == "csv":
        # Array-valued columns can't be hashed; only csv types are guaranteed scalar.
        df = df.drop_duplicates(ignore_index=True)
    if len(df) == 0:
        raise NoValidProblemsError(
            f"{cls.__name__}: none of {n_tried} candidate params passed check_solution()")
    if verbose:
        print(f"{cls.__name__}: {len(df)} valid of {n_tried} candidates")
    return df


def save(df, cls, data_dir=None):
    path = data_path(cls, data_dir)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if cls.data_format == "csv":
        df.to_csv(path, header=True, index=False)
    elif cls.data_format == "pkl":
        df.to_pickle(path)
    else:
        raise ValueError(f"{cls.__name__}: unknown data_format {cls.data_format!r}")
    return path


def load_valid(cls, data_dir=None):
    path = data_path(cls, data_dir)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found; generate it first (e.g. python -m problems {cls.__name__})")
    if cls.data_format == "csv":
        return pd.read_csv(path)
    return pd.read_pickle(path)


def dependency_order(registry, names):
    """Return `names` plus everything they depend on, dependencies first."""
    order, visiting, done = [], set(), set()

    def visit(name):
        if name in done:
            return
        if name in visiting:
            raise ValueError(f"circular depends_on involving {name}")
        visiting.add(name)
        for dep in registry[name].depends_on:
            visit(dep)
        visiting.discard(name)
        done.add(name)
        order.append(name)

    for name in names:
        visit(name)
    return order


def generate_all(registry, names=None, data_dir=None, dry_run=False, with_deps=False):
    """
    Generate and save valid params for `names` (default: every registered type),
    in dependency order. With with_deps=True, also regenerate dependencies that
    weren't explicitly requested; otherwise existing dependency files are reused.
    """
    requested = list(names) if names else registry.names()
    order = dependency_order(registry, requested)
    if not with_deps:
        order = [n for n in order if n in requested]
    results = {}
    for name in order:
        cls = registry[name]
        df = generate(cls, verbose=True)
        results[name] = len(df)
        if not dry_run:
            print(f"  -> {save(df, cls, data_dir)}")
    return results


def main(registry, argv=None):
    """Command-line entry point. A course's problems/__main__.py can be just `main(REGISTRY)`."""
    parser = argparse.ArgumentParser(description="Generate valid parameter sets for problem types.")
    parser.add_argument("names", nargs="*", help="problem types to generate (default: all)")
    parser.add_argument("--data-dir", default=None, help="output directory (default: config.data_dir)")
    parser.add_argument("--dry-run", action="store_true", help="count valid rows without writing files")
    parser.add_argument("--with-deps", action="store_true", help="also regenerate depends_on types")
    parser.add_argument("--list", action="store_true", help="list registered problem types and exit")
    args = parser.parse_args(argv)
    if args.list:
        for name in registry.names():
            print(name)
        return
    unknown = [n for n in args.names if n not in registry]
    if unknown:
        parser.error(f"unknown problem types: {', '.join(unknown)}")
    generate_all(registry, args.names, data_dir=args.data_dir,
                 dry_run=args.dry_run, with_deps=args.with_deps)
