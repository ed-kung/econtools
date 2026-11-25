"""
Base class and course-level configuration for auto-generated econ problems.

A problem type is a subclass of GenericProblem that:
  - declares `default_params`
  - implements `build(rng)`, filling self.setup_list / self.question_list / self.sol
  - optionally implements `check_solution()` to reject "ugly" parameterizations
  - optionally implements the classmethod `candidate_params(rng)`, yielding
    parameter dicts to try when generating the set of valid problems

Each entry of setup_list is a dict with keys:
    'setup', 'online_setup'
Each entry of question_list is a dict with keys:
    'question', 'online_question', 'answer', 'online_answer', 'MCQ'
These are the keys read by econtools.problems.formats.
"""

import os
from dataclasses import dataclass, field

import numpy as np

from econtools.assignments.mcq import MCQ, generate_distractors
from econtools.math.scaled import Scaled


@dataclass
class ProblemConfig:
    # URL prefix for graph images in online (HTML) output, e.g. "/CSUN-Econ-310/assets/images/graphs"
    image_url_prefix: str = ""
    # Path prefix for graph images in LaTeX output (relative to the .tex file); "" = same directory
    latex_image_prefix: str = ""
    # Directory where draw_graphs() writes PNG files by default
    image_dir: str = "."
    # Directory holding the <Type>.csv / <Type>.pkl files of valid parameters
    data_dir: str = "."
    # Width used in \includegraphics
    latex_image_width: str = "3in"
    # Extra settings a course may want to stash
    extra: dict = field(default_factory=dict)


# Module-level config. Each course sets this once, e.g. in its problems/__init__.py:
#     from econtools.problems.base import config
#     config.image_url_prefix = "/CSUN-Econ-310/assets/images/graphs"
config = ProblemConfig()


def _join_url(prefix, filename):
    if not prefix:
        return filename
    return prefix.rstrip("/") + "/" + filename


class GenericProblem:
    # --- class-level declarations (override in subclasses) ---
    default_params: dict = {}
    data_format: str = "parquet"   
    depends_on: tuple = ()         # names of problem types whose data must be generated first
    seed: int = 123                # default seed used when generating valid params
    default_name: str = None       # default instance name; falls back to snake_case of class name

    def __init__(self, params=None, rng=None, name=None):
        self.name = name if name is not None else self._default_instance_name()
        self.rng = rng if rng is not None else np.random.default_rng()
        self.params = self._merge_params(params)
        self.sol = {}
        self.setup_list = []
        self.question_list = []
        self.axes = {}             # suffix -> Axis, drawn by draw_graphs()
        self.build(self.rng)

    # --- hooks ---
    def build(self, rng):
        raise NotImplementedError(f"{type(self).__name__} must implement build(rng)")

    def check_solution(self):
        return True

    @classmethod
    def candidate_params(cls, rng):
        """Yield parameter dicts to try when generating valid problems."""
        return
        yield

    # --- params ---
    def _merge_params(self, params):
        defaults = dict(self.default_params)
        if not params:
            return defaults
        return {k: params.get(k, v) for k, v in defaults.items()}

    @classmethod
    def _default_instance_name(cls):
        if cls.default_name:
            return cls.default_name
        out = []
        for i, ch in enumerate(cls.__name__):
            if ch.isupper() and i > 0:
                out.append("_")
            out.append(ch.lower())
        return "".join(out)

    def record(self):
        """The row written to the valid-params data file."""
        return self.params | self.sol

    # --- builder helpers ---
    def add_setup(self, setup, online_setup=None):
        if online_setup is None:
            online_setup = latex_to_online(setup)
        self.setup_list.append({"setup": setup, "online_setup": online_setup})
        return len(self.setup_list) - 1

    def add_question(self, question, answer, online_question=None, online_answer=None, mcq=None):
        answer = format_answer(answer)
        if online_answer is not None:
            online_answer = format_answer(online_answer)
        if online_question is None:
            online_question = latex_to_online(question)
        if online_answer is None:
            online_answer = latex_to_online(answer)
        self.question_list.append({
            "question": question,
            "online_question": online_question,
            "answer": answer,
            "online_answer": online_answer,
            "MCQ": mcq,
        })
        return len(self.question_list) - 1

    def add_numeric_question(self, question, answer, rng, scale=1, numtype='', K=4,
                             online_question=None, **mcq_kw):
        """
        Add a numerical question with K generated distractors. Answers are shown
        multiplied by `scale` and formatted by `numtype` ('' or '$', etc.).
        Extra keyword arguments override the MCQ defaults (sort, horz, ...).
        """
        answers = generate_distractors(answer, K=K, rng=rng)
        opts = dict(solution=0, shuffle=False, sort=True, numerical=True, horz=True) | mcq_kw
        mcq = MCQ(question, answers, rng=rng, scale=scale, numtype=numtype, **opts)
        return self.add_question(question, answer=answer, online_question=online_question,
                                 online_answer=str(Scaled(answer, scale, numtype)), mcq=mcq)

    # --- graphs ---
    def image_filename(self, suffix):
        return f"{self.name}_{suffix}.png" if suffix else f"{self.name}.png"

    def latex_image(self, suffix, width=None):
        width = width or config.latex_image_width
        path = config.latex_image_prefix + self.image_filename(suffix)
        return f"\\begin{{center}}\n\\includegraphics[width={width}]{{{path}}}\n\\end{{center}}\n"

    def online_image(self, suffix):
        return f'<img src="{_join_url(config.image_url_prefix, self.image_filename(suffix))}">'

    def add_axis(self, suffix, axis):
        """Register an Axis to be saved as <name>_<suffix>.png by draw_graphs()."""
        self.axes[suffix] = axis
        return axis

    def draw_graphs(self, out_dir=None, **draw_kw):
        """Save every registered axis to out_dir (defaults to config.image_dir)."""
        from matplotlib import pyplot as plt
        out_dir = out_dir or config.image_dir
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        for suffix, axis in self.axes.items():
            path = os.path.join(out_dir, self.image_filename(suffix))
            fig, _ = axis.draw(saveas=path, **draw_kw)
            plt.close(fig)
            paths.append(path)
        return paths

    # --- inspection ---
    def show_setups(self):
        for i, s in enumerate(self.setup_list):
            print(f"{i}: {s}")

    def show_questions(self):
        for i, q in enumerate(self.question_list):
            print(f"{i}: {q}")


def format_answer(x):
    """
    Convert an answer to a display string. Strings pass through unchanged;
    numbers (Python or numpy) are formatted cleanly: integral floats drop the
    trailing ".0" and float round-off noise is trimmed.
    """
    if isinstance(x, str):
        return x
    if isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        x = round(x, 10)
        if x.is_integer():
            return str(int(x))
    return str(x)


def latex_to_online(tex):
    """
    Best-effort conversion of a LaTeX snippet to the online (MathJax/HTML) form:
    display environments are wrapped in $$...$$ and align* becomes align.
    Pass an explicit online version when this isn't good enough.
    """
    out = tex
    for env in ("align*", "equation*", "gather*"):
        base = env.rstrip("*")
        out = out.replace(f"\\begin{{{env}}}", f"$$\\begin{{{base}}}")
        out = out.replace(f"\\end{{{env}}}", f"\\end{{{base}}}$$")
    return out
