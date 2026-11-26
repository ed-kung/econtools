"""
Named things for auto-generated problems: people, goods, countries, firms, cities.

The possible values of each class live in a CSV file under ./data, one row per
entry. Cells holding several values (tags) separate them with ';'.

    from econtools.entities import Person, Good

    person = Person.sample(rng)                          # one random person
    g1, g2 = Good.sample(rng, 2, tags="food")            # two distinct foods
    other = Person.sample(rng, exclude=[person])         # never the same as person
    widget = Good.get("widget")                          # a specific entry
    price = widget.random_price(rng)                     # integer in [pmin, pmax] * pscale

    f"{person.name} sells {g1.plural} to {person.possessive} friends"

Sampling only uses the numpy Generator passed in, so seeded generation is
reproducible. Entities are frozen dataclasses; to_dict()/from_dict() convert
them to plain data, which GenericProblem uses to store them in parquet.
"""

import csv
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import numpy as np

DATA_DIR = Path(__file__).parent / "data"


def _split(cell):
    """'a; b;c' -> ['a', 'b', 'c']; blank -> []."""
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def _num(s):
    x = float(s)
    return int(x) if x.is_integer() else x


def _plain(x):
    """numpy scalars -> Python scalars (parquet round trips return numpy types)."""
    return x.item() if isinstance(x, np.generic) else x


def _tag_set(tags):
    if tags is None:
        return set()
    if isinstance(tags, str):
        return {tags}
    return set(tags)


@dataclass(frozen=True)
class Entity:
    csv_name: ClassVar[str] = ""
    key_field: ClassVar[str] = "name"
    _cache: ClassVar[dict] = {}

    # --- data ---
    @classmethod
    def csv_path(cls):
        return DATA_DIR / cls.csv_name

    @classmethod
    def _all_rows(cls):
        if cls not in Entity._cache:
            with open(cls.csv_path(), newline="", encoding="utf-8") as f:
                rows = [{k.strip(): (v or "").strip() for k, v in row.items()}
                        for row in csv.DictReader(f)]
            rows = [r for r in rows if r.get(cls.key_field)]
            keys = [r[cls.key_field] for r in rows]
            dupes = {k for k in keys if keys.count(k) > 1}
            if dupes:
                raise ValueError(f"{cls.csv_path()}: duplicate {cls.key_field} {sorted(dupes)}")
            Entity._cache[cls] = rows
        return Entity._cache[cls]

    @classmethod
    def reload(cls):
        """Forget cached CSV contents (e.g. after editing a CSV in a live session)."""
        Entity._cache.pop(cls, None)

    @classmethod
    def rows(cls, tags=None):
        """CSV rows (dicts of strings) carrying all of the given tags."""
        want = _tag_set(tags)
        return [r for r in cls._all_rows() if want <= set(_split(r.get("tags")))]

    @classmethod
    def keys(cls, tags=None):
        return [r[cls.key_field] for r in cls.rows(tags)]

    @classmethod
    def _from_row(cls, row):
        """Build an instance from a CSV row. Override when a row needs parsing."""
        names = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in row.items() if k in names})

    # --- construction ---
    @classmethod
    def get(cls, key):
        """The entry whose key field equals `key`."""
        for r in cls._all_rows():
            if r[cls.key_field] == key:
                return cls._from_row(r)
        raise KeyError(f"{cls.__name__}: no entry {key!r} in {cls.csv_path()}")

    @classmethod
    def sample(cls, rng, n=None, tags=None, exclude=()):
        """
        Random distinct entries. n=None returns one instance; n=k a tuple of k.
        `tags`: only rows carrying all these tags. `exclude`: instances or keys to skip.
        """
        skip = {e.key if isinstance(e, Entity) else e for e in exclude}
        pool = [r for r in cls.rows(tags) if r[cls.key_field] not in skip]
        k = 1 if n is None else n
        if k > len(pool):
            raise ValueError(f"{cls.__name__}.sample: asked for {k} but only {len(pool)} "
                             f"match tags={tags!r} excluding {sorted(skip)}")
        idx = rng.choice(len(pool), size=k, replace=False)
        out = tuple(cls._from_row(pool[int(i)]) for i in idx)
        return out[0] if n is None else out

    # --- serialization ---
    def to_dict(self):
        return {f.name: _plain(getattr(self, f.name)) for f in dataclasses.fields(self)}

    @classmethod
    def from_dict(cls, d):
        names = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: _plain(v) for k, v in dict(d).items() if k in names})

    @property
    def key(self):
        return getattr(self, self.key_field)

    def __str__(self):
        return str(self.key)


# subject, object, possessive (adjective), possessive pronoun, reflexive
PRONOUNS = {
    "he": ("he", "him", "his", "his", "himself"),
    "she": ("she", "her", "her", "hers", "herself"),
    "they": ("they", "them", "their", "theirs", "themselves"),
}


@dataclass(frozen=True)
class Person(Entity):
    """A person. CSV: people.csv (name, pronouns, tags); pronouns is he/she/they."""
    csv_name: ClassVar[str] = "people.csv"
    name: str
    pronouns: str = "they"

    def __post_init__(self):
        if self.pronouns not in PRONOUNS:
            raise ValueError(f"Person {self.name!r}: pronouns must be one of {list(PRONOUNS)}, "
                             f"got {self.pronouns!r}")

    @property
    def subject(self):             # he / she / they
        return PRONOUNS[self.pronouns][0]

    @property
    def object(self):              # him / her / them
        return PRONOUNS[self.pronouns][1]

    @property
    def possessive(self):          # his / her / their (+ noun)
        return PRONOUNS[self.pronouns][2]

    @property
    def possessive_pronoun(self):  # his / hers / theirs (standalone)
        return PRONOUNS[self.pronouns][3]

    @property
    def reflexive(self):           # himself / herself / themselves
        return PRONOUNS[self.pronouns][4]


@dataclass(frozen=True)
class Good(Entity):
    """
    A good. CSV: goods.csv
        (market, singular, plural, tags, pscale, qscale, pmin, pmax, qmin, qmax, article)

    market is the name of the good overall ("the market for coffee"); singular and
    plural name its unit ("$20 per bag", "3 bags"). market is the key used by get().

    pscale/qscale are the good's typical price and quantity per unit (e.g. per grid
    unit of a graph axis, or for Scaled). pmin..pmax and qmin..qmax are integer
    ranges, in those units, for drawing a random price or quantity:
        good.random_price(rng)  ==  rng.integers(pmin, pmax + 1) * pscale
    Blank cells use DEFAULTS. article overrides the computed a/an for the unit.

    Unit phrases (coffee: bag/bags; cars: car/cars):
        good.unit        'bag of coffee'   'car'
        good.units       'bags of coffee'  'cars'
        good.a           'a bag of coffee' 'a car'
        good.amount(3)   '3 bags of coffee' ;  good.amount(3, full=False) -> '3 bags'
    The "of <market>" is left off when the unit already names the good, i.e. when
    market starts with singular (cars/car, pizza/pizza, USB sticks/USB stick).
    """
    csv_name: ClassVar[str] = "goods.csv"
    key_field: ClassVar[str] = "market"
    DEFAULTS: ClassVar[dict] = {"pscale": 1, "qscale": 1, "pmin": 1, "pmax": 10, "qmin": 1, "qmax": 10}

    market: str
    singular: str = ""
    plural: str = ""
    pscale: float = 1
    qscale: float = 1
    pmin: int = 1
    pmax: int = 10
    qmin: int = 1
    qmax: int = 10
    article: str = ""

    def __post_init__(self):
        if not self.singular:
            object.__setattr__(self, "singular", self.market)
        if not self.plural:
            object.__setattr__(self, "plural", self.singular + "s")
        if self.pmin > self.pmax or self.qmin > self.qmax:
            raise ValueError(f"Good {self.market!r}: need pmin <= pmax and qmin <= qmax")

    @classmethod
    def _from_row(cls, row):
        nums = {k: _num(row[k]) if row.get(k) else v for k, v in cls.DEFAULTS.items()}
        return cls(market=row["market"], singular=row.get("singular", ""), plural=row.get("plural", ""),
                   article=row.get("article", ""), **nums)

    def random_price(self, rng):
        """A random price: an integer in [pmin, pmax] times pscale."""
        return int(rng.integers(self.pmin, self.pmax + 1)) * self.pscale

    def random_quantity(self, rng):
        """A random quantity: an integer in [qmin, qmax] times qscale."""
        return int(rng.integers(self.qmin, self.qmax + 1)) * self.qscale

    # --- unit phrases ---
    @property
    def _unit_names_good(self):
        return self.market.lower().startswith(self.singular.lower())

    @property
    def unit(self):
        """'bag of coffee', or just 'car' when the unit already names the good."""
        return self.singular if self._unit_names_good else f"{self.singular} of {self.market}"

    @property
    def units(self):
        """'bags of coffee', or just 'cars' when the unit already names the good."""
        return self.plural if self._unit_names_good else f"{self.plural} of {self.market}"

    @property
    def a(self):
        """'a bag of coffee', 'a car', 'an apple' (article column overrides a/an)."""
        art = self.article or ("an" if self.singular[:1].lower() in "aeiou" else "a")
        return f"{art} {self.unit}"

    def amount(self, n, full=True):
        """'1 bag of coffee', '3 bags of coffee'; full=False gives '3 bags'."""
        one = n == 1
        if full:
            return f"{n} {self.unit if one else self.units}"
        return f"{n} {self.singular if one else self.plural}"


@dataclass(frozen=True)
class Country(Entity):
    """A country. CSV: countries.csv (name, adjective, tags)."""
    csv_name: ClassVar[str] = "countries.csv"
    name: str
    adjective: str = ""


@dataclass(frozen=True)
class Firm(Entity):
    """A firm. CSV: firms.csv (name, tags)."""
    csv_name: ClassVar[str] = "firms.csv"
    name: str


@dataclass(frozen=True)
class City(Entity):
    """A city. CSV: cities.csv (name, country, tags)."""
    csv_name: ClassVar[str] = "cities.csv"
    name: str
    country: str = ""
