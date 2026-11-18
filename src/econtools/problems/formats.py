"""
Render a built problem into an output format.

These functions only read problem.setup_list and problem.question_list
(see econtools.problems.base for the dict keys); they never build anything.
"""

import copy

from econtools.assignments.latex import Multipart, RawLatex


def get_online_format(problem, setup_id=0, question_ids=None):
    """HTML setup and solution strings for the course website."""
    if question_ids is None:
        question_ids = range(len(problem.question_list))
    setup = problem.setup_list[setup_id]['online_setup']
    setup = f'<p>{setup}</p>\n' if len(setup) > 0 else ''
    solution = ''
    for i, qid in enumerate(question_ids, start=1):
        q = problem.question_list[qid]
        setup += f'<p>{i}. ' + q['online_question'] + '</p>\n'
        solution += f'<p>{i}. ' + q['online_answer'] + '</p>\n'
    return {'setup': setup, 'solution': solution}


def get_multipart_sa(problem, setup_id=0, question_ids=None):
    """Short-answer multipart question: setup followed by an a./b./c. list."""
    if question_ids is None:
        question_ids = range(len(problem.question_list))
    setup = problem.setup_list[setup_id]['setup']
    assert len(setup) > 0, "multipart questions need a non-empty setup"
    t = "\\begin{q}\n"
    t += setup
    t += "\\begin{enumerate}[a.]\n"
    for qid in question_ids:
        t += "\\item " + problem.question_list[qid]['question'] + "\n"
    t += "\\end{enumerate}\n"
    t += "\\end{q}\n"
    return RawLatex(t)


def get_multipart_mcq(problem, setup_id=0, question_ids=None):
    """Multiple-choice multipart question: setup followed by one MCQ per part."""
    if question_ids is None:
        question_ids = range(len(problem.question_list))
    setup = problem.setup_list[setup_id]['setup']
    assert len(setup) > 0, "multipart questions need a non-empty setup"
    multipart = Multipart()
    multipart.add(RawLatex(setup))
    for qid in question_ids:
        mcq = problem.question_list[qid]['MCQ']
        if mcq is None:
            raise ValueError(f"question {qid} of {type(problem).__name__} has no MCQ form")
        multipart.add(mcq)
    return multipart


def get_single_sa(problem, setup_id=0, question_id=0):
    """A single short-answer question with the setup prepended."""
    setup = problem.setup_list[setup_id]['setup']
    question = problem.question_list[question_id]['question']
    if len(setup) > 0:
        question = setup + "\n\n" + question
    t = "\\begin{q}\n"
    t += question
    t += "\\end{q}\n"
    return RawLatex(t)


def get_single_mcq(problem, setup_id=0, question_id=0):
    """A single MCQ with the setup prepended. Returns a copy; the stored MCQ is unchanged."""
    setup = problem.setup_list[setup_id]['setup']
    mcq = problem.question_list[question_id]['MCQ']
    if mcq is None:
        raise ValueError(f"question {question_id} of {type(problem).__name__} has no MCQ form")
    mcq = copy.copy(mcq)
    if len(setup) > 0:
        mcq.question = setup + "\n\n" + mcq.question
    return mcq
