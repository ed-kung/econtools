import numpy as np

rng = np.random.default_rng()

class MCQ:
    def __init__(self, question, answers, solution=0, horz=False, shuffle=True, sort=False, rng=rng, numerical=False):
        self.question = question     # question setup
        self.answers = answers       # list of answers
        self.solution = solution     # index of the correct answer
        self.horz = horz             # whether display answers horizontally (default false)
        self.numerical = numerical   # whether answers are numerical (default false)
        # sort: whether to sort the answers alphabetically (default false)
        # shuffle: whether to shuffle the answers (default true)
        
        if sort:
            self.answers = answers.copy()
            sortindex = np.argsort(answers)
            for i in range(len(answers)):
                self.answers[i] = answers[sortindex[i]]
            self.solution = sortindex.tolist().index(solution)
        elif shuffle:
            perm = rng.permutation(len(self.answers))
            tempa = self.answers.copy()
            for i in range(len(self.answers)):
                self.answers[perm[i]] = tempa[i]
            self.solution = perm[self.solution]
        
        # Check duplicates
        if len(self.answers)!=len(set(self.answers)):
            print(self.answers)
            print("Error: Duplicate answers!")
            raise
    
    def texify(self, solutions=False):
        question = self.question
        answers = self.answers
        t = "\\begin{q}\n" + question + "\n\n"
        if self.horz:
            for i in range(len(answers)):
                myans = answers[i]
                if self.numerical:
                    myans = f"{myans:,g}"
                t+= f"~ {chr(97+i)}) {myans} \n"
        else:
            t+='\\begin{enumerate}[(a)]\n'
            for i in range(len(answers)):
                myans = answers[i]
                if self.numerical:
                    myans = f"{myans:,g}"
                t+=f"  \\item {myans} \n"
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
   