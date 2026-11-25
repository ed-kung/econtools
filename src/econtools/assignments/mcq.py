import numpy as np
from econtools.math.scaled import Scaled, format_number, _check_numtype

rng = np.random.default_rng()

class MCQ:
    def __init__(self, question, answers, solution=0, horz=False, shuffle=True, sort=False, rng=rng, numerical=False, scale=None, numtype=''):
        self.question = question     # question setup
        self.answers = list(answers) # list of answers (raw values: numbers stay numbers so they sort numerically)
        self.solution = solution     # index of the correct answer
        self.horz = horz             # whether display answers horizontally (default false)
        self.scale = scale           # scale factor to use with Scaled class (answers are then grid values)
        self.numtype = numtype       # passed to Scaled: '$' adds dollar prefix; '%' converts to percentage with % suffix
        _check_numtype(numtype)
        # whether answers are numerical (default false); implied by scale, numtype, or Scaled answers
        self.numerical = (numerical or scale is not None or numtype != ''
                          or any(isinstance(a, Scaled) for a in self.answers))
        # sort: whether to sort the answers, numerically if numerical, else alphabetically (default false)
        # shuffle: whether to shuffle the answers (default true)

        if sort:
            key = self._numeric_key if self.numerical else (lambda a: a)
            sortindex = sorted(range(len(self.answers)), key=lambda i: key(self.answers[i]))
            self.answers = [self.answers[i] for i in sortindex]
            self.solution = sortindex.index(solution)
        elif shuffle:
            perm = rng.permutation(len(self.answers))
            tempa = self.answers.copy()
            for i in range(len(self.answers)):
                self.answers[perm[i]] = tempa[i]
            self.solution = perm[self.solution]

        # Stringify only after ordering, so prefixes/suffixes/separators don't affect the sort
        self.answer_strings = [self.format_answer(a) for a in self.answers]

        # Check duplicates on the displayed strings (distinct numbers can format identically)
        if len(self.answer_strings)!=len(set(self.answer_strings)):
            raise ValueError(f"MCQ: duplicate answers: {self.answer_strings}")

    @staticmethod
    def _numeric_key(a):
        return float(a.real) if isinstance(a, Scaled) else float(a)

    def format_answer(self, a):
        # Convert a single (raw) answer to its LaTeX display string.
        # Formatting (k/m/B/T, $ prefix, % suffix) lives in econtools.math.scaled.
        if not self.numerical:
            return str(a)
        if isinstance(a, Scaled):
            if self.numtype and a.numtype != self.numtype:
                a = Scaled(a.grid, a.scale, self.numtype)
            s = str(a)
        elif self.scale is not None:
            s = str(Scaled(a, self.scale, self.numtype))
        else:
            s = format_number(a, self.numtype, human=False)
        return s.replace('$', '\\$').replace('%', '\\%')

    def texify(self, solutions=False):
        question = self.question
        answers = self.answer_strings
        t = "\\begin{q}\n" + question + "\n\n"
        if self.horz:
            for i in range(len(answers)):
                t+= f"~ {chr(97+i)}) {answers[i]} \n"
        else:
            t+='\\begin{enumerate}[(a)]\n'
            for i in range(len(answers)):
                t+=f"  \\item {answers[i]} \n"
            t+='\\end{enumerate}\n'
        if solutions:
            t+= f"\n{{\\color{{red}} Answer: {chr(97+self.solution)} }}\n"
        t+= "\\end{q}\n"
        return t
        
def generate_distractors(x, K=4, delta=None, type='add', rng=rng, must_positive=False):
    if not delta:
        if type=='add':
            if np.abs(x)>=10: delta = np.round(0.1*np.abs(x))
            elif np.abs(x)>=4: delta = 1
            elif np.abs(x)>=2: delta = 0.5
            elif np.abs(x)>=1: delta = 0.1
            elif np.abs(x)>0: delta = 0.1*np.abs(x)
            else: delta = 1
        else:
            delta = 2
    
    max_tries = 100
    for i in range(max_tries):
        nless = rng.integers(K)
        nmore = K - nless - 1
        answers = [x]
        for i in range(nless):
            if type=='mul':
                answers.append(x*delta**(-i-1))
            if type=='add':
                answers.append(x - delta*(i+1))
        for i in range(nmore):
            if type=='mul':
                answers.append(x*delta**(i+1))
            if type=='add':
                answers.append(x + delta*(i+1))
        
        any_negative = False
        for ans in answers:
            if ans<0:
                any_negative = True
        if must_positive and any_negative:
            continue
        else:
            return answers
    raise ValueError(
        f"generate_distractors: could not generate {K} non-negative answers around x={x} "
        f"(delta={delta}) in {max_tries} tries"
    )
   