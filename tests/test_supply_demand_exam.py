"""
Test script: graphing + exam building.

Draws a supply and demand diagram with graphs.primitives.Line (labelstyle="label"),
uses math.scaled.Scaled with a price scale of $5 per grid point and a quantity
scale of 1M units per grid point, and builds a single multipart exam question
asking for the equilibrium price and quantity. Writes the PDFs to ./tests.

Run from the repo root:
    python tests/test_supply_demand_exam.py
"""

import os
import shutil
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

plt.rcParams['figure.figsize'] = (6, 6)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(TESTS_DIR), "src"))

from econtools.graphs.axis import Axis
from econtools.graphs.primitives import Line
from econtools.math.scaled import Scaled
from econtools.assignments.latex import Exam, Multipart, RawLatex
from econtools.assignments.mcq import MCQ, generate_distractors

PSCALE = 5            # $5 per grid point
QSCALE = 1_000_000    # 1M units per grid point
N = 13                # grid points per axis

# Curves in grid units: demand P = 12 - Q, supply P = 2 + Q
D_INTERCEPT, D_SLOPE = 12, -1
S_INTERCEPT, S_SLOPE = 2, 1


def scaled_line(intercept, slope):
    """Return (intercept, slope) as Scaled values in real units."""
    b = Scaled(intercept, PSCALE)
    m = Scaled(slope, PSCALE) / Scaled(1, QSCALE)
    return b, m


def solve_equilibrium():
    bd, md = scaled_line(D_INTERCEPT, D_SLOPE)
    bs, ms = scaled_line(S_INTERCEPT, S_SLOPE)
    q = (bd - bs) / (ms - md)
    p = bs + ms * q
    return p, q, (bd, md), (bs, ms)


def draw_diagram(saveas):
    # the axis plots in grid units; its scales only relabel the ticks
    axis = Axis(xn=N, yn=N, xscale=QSCALE, yscale=PSCALE,
                xlab="Quantity (units)", ylab="Price")
    for (b, m), label, color in (((D_INTERCEPT, D_SLOPE), "Demand", "tab:blue"),
                                 ((S_INTERCEPT, S_SLOPE), "Supply", "tab:red")):
        axis.add(Line(m, b, linewidth=2, color=color, label=label))

    fig, ax = axis.draw(labelstyle="label")

    fig.savefig(saveas, bbox_inches="tight")
    plt.close(fig)


def build_exam(p, q, figure_file, rng):
    exam = Exam("ECON 101 Test Exam", version="A", time=10)

    question = Multipart()
    question.add(RawLatex(
        "\\noindent Use the supply and demand diagram below to answer the following questions.\n\n"
        "\\begin{center}\n"
        f"\\includegraphics[width=0.6\\textwidth]{{{figure_file}}}\n"
        "\\end{center}\n\n"
    ))

    p_grids = generate_distractors(int(p.grid), K=4, delta=1, rng=rng, must_positive=True)
    p_answers = [f"\\${Scaled(g, PSCALE)}" for g in p_grids]
    question.add(MCQ("What is the equilibrium price?", p_answers, solution=0, rng=rng))

    q_grids = generate_distractors(int(q.grid), K=4, delta=1, rng=rng, must_positive=True)
    q_answers = [f"{Scaled(g, QSCALE)} units" for g in q_grids]
    question.add(MCQ("What is the equilibrium quantity?", q_answers, solution=0, rng=rng))

    exam.add(question)
    return exam, p_answers[0], q_answers[0]


def main():
    p, q, demand, supply = solve_equilibrium()

    # Scaled arithmetic checks
    assert p == Scaled(7, PSCALE) and p.real == 35, repr(p)
    assert q == Scaled(5, QSCALE) and q.real == 5_000_000, repr(q)
    assert str(p) == "35" and str(q) == "5m"

    figure_file = "supply_demand.pdf"
    draw_diagram(os.path.join(TESTS_DIR, figure_file))
    assert os.path.exists(os.path.join(TESTS_DIR, figure_file))

    rng = np.random.default_rng(0)
    exam, p_correct, q_correct = build_exam(p, q, figure_file, rng)

    tex = exam.texify()
    assert "Supply" not in tex  # labels live in the graph, not the tex
    assert p_correct in tex and q_correct in tex
    assert "Answer:" not in tex
    assert "Answer:" in exam.texify(solutions=True)

    if shutil.which("pdflatex") is None:
        print("pdflatex not found; skipping PDF compilation")
        return

    for name, solutions in (("test_exam", False), ("test_exam_solutions", True)):
        exam.print_pdf(name, TESTS_DIR, solutions=solutions)
        pdf = os.path.join(TESTS_DIR, f"{name}.pdf")
        assert os.path.exists(pdf), f"{pdf} was not produced"
        print(f"Wrote {pdf}")

    print(f"Equilibrium: price = ${p}, quantity = {q} units")
    print("All checks passed.")


if __name__ == "__main__":
    main()
