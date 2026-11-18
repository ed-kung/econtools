"""
Look up problem types by name.

Each course keeps its own Registry, filled by discover() from the course's
problems package (one module per problem type):

    # <course>/problems/__init__.py
    from econtools.problems.registry import Registry, discover
    REGISTRY = Registry()
    discover(__name__, REGISTRY)

Problem classes can also opt in explicitly with @REGISTRY.register.
"""

import importlib
import inspect
import pkgutil

import numpy as np

from econtools.problems.base import GenericProblem
from econtools.problems import generate as _generate


class Registry:
    def __init__(self):
        self._types = {}

    def register(self, cls):
        """Register a GenericProblem subclass under its class name. Usable as a decorator."""
        if not (inspect.isclass(cls) and issubclass(cls, GenericProblem)):
            raise TypeError(f"{cls!r} is not a GenericProblem subclass")
        name = cls.__name__
        existing = self._types.get(name)
        if existing is not None and existing is not cls:
            raise ValueError(
                f"problem type {name!r} already registered from {existing.__module__}")
        self._types[name] = cls
        return cls

    def __getitem__(self, name):
        try:
            return self._types[name]
        except KeyError:
            raise KeyError(f"unknown problem type {name!r}") from None

    def __contains__(self, name):
        return name in self._types

    def __iter__(self):
        return iter(self._types)

    def __len__(self):
        return len(self._types)

    def names(self):
        return list(self._types)

    def as_dict(self):
        """Plain {name: class} dict, e.g. for a legacy PROBLEM_TYPES alias."""
        return dict(self._types)

    # --- name-based entry points ---
    def load_problem(self, problem_str, params=None, name=None, rng=None):
        return self[problem_str](params=params, rng=rng, name=name)

    def sample_problem(self, problem_str, rng=None, name=None, data_dir=None, **filters):
        """
        Draw one row from the type's valid-params file and build that problem.
        `filters` restrict rows by column value, e.g. sample_problem('X', rng, xunit=1).
        """
        rng = rng if rng is not None else np.random.default_rng()
        cls = self[problem_str]
        df = _generate.load_valid(cls, data_dir)
        for col, val in filters.items():
            df = df[df[col] == val]
        if len(df) == 0:
            raise ValueError(f"no rows of {problem_str} match {filters}")
        params = dict(df.sample(1, random_state=rng).iloc[0])
        return cls(params=params, rng=rng, name=name)

    def show_menu(self, problem_str, params=None, name=None, rng=None):
        prob = self.load_problem(problem_str, params=params, name=name, rng=rng)
        print(prob.params)
        print(prob.sol)
        for i, s in enumerate(prob.setup_list):
            print(f"{i}: {s['setup']}".replace('\n', ' '))
            print("")
        for i, q in enumerate(prob.question_list):
            print(f"{i}: {q['question']}".replace('\n', ' '))
            print("")
        return prob


def discover(package_name, registry):
    """
    Import every module in `package_name` (recursively) and register each
    GenericProblem subclass defined there. Returns the registry.
    """
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        raise ValueError(f"{package_name} is a module, not a package")
    for info in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
        if info.name.rsplit(".", 1)[-1].startswith("_"):
            continue  # skip __main__, _private helpers
        module = importlib.import_module(info.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, GenericProblem) and obj is not GenericProblem
                    and obj.__module__ == module.__name__):
                registry.register(obj)
    return registry
