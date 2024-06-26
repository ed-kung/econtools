import os

DEFAULT_PREAMBLE = """
\\documentclass[11pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=1in]{geometry}
\\usepackage{pgfplots}
\\pgfplotsset{compat=1.11}
\\usepgfplotslibrary{fillbetween}
\\usetikzlibrary{patterns}
\\usetikzlibrary{arrows.meta}
\\usetikzlibrary{positioning}
\\usetikzlibrary{automata}
\\usepackage{amsmath}
\\usepackage{enumerate}
\\usepackage{setspace}
\\usepackage{array}
\\usepackage{multirow}
\\usepackage{tabularx}
\\usepackage{booktabs}
\\usepackage{xfp}
\\usepackage[shortlabels]{enumitem}
\\usepackage[parfill]{parskip}
\\usepackage{pifont}
\\usepackage{wasysym}
\\usepackage{amssymb}
\\usepackage{hyperref}
\\linespread{1}
\\setlist[enumerate]{topsep=0.5ex, itemsep=0.5ex}
\\renewcommand{\\arraystretch}{1.15}
\\newcolumntype{C}[1]{>{\\centering\\let\\newline\\\\\\arraybackslash\\hspace{0pt}}m{#1}}
\\newcommand{\\fb}{\\rule{2cm}{0.15mm} }
\\setlength{\\parskip}{\\medskipamount}
\\newcommand{\\@minipagerestore}{\\setlength{\\parskip}{\\medskipamount}}
\\date{}
\\newcounter{qcounter}
\\newenvironment{q}[0]{
    \\stepcounter{qcounter}
    \\begin{enumerate}
    \\item[\\arabic{qcounter}.]
}{
    ~
    \\end{enumerate}
}
"""

class Document:
    def __init__(self, separator='\n\n'):
        self.items = []
        self.separator = separator
    
    def add(self, item):
        self.items.append(item)
    
    def texify(self, solutions=False):
        t = DEFAULT_PREAMBLE
        t+= "\\begin{document}\n\n"
        
        for item in self.items:
            t+="\\begin{minipage}{\\textwidth}\n"
            t+=item.texify(solutions)
            t+=self.separator
            t+="\\end{minipage}\n\n"
        
        t+="\\end{document}\n\n"
        return t
    
    def print_pdf(self, filename, output_dir, solutions=False):
        t = self.texify(solutions)
        with open(os.path.join(output_dir, f"{filename}.tex"), 'w') as f:
            f.write(t)
        os.chdir(output_dir)
        os.system(f"pdflatex {filename}")

class Homework(Document):
    def __init__(self, title, due_date, separator='\\vspace{0.5cm}\n\\hrule\n\\vspace{0.5cm}'):
        self.items = []
        self.separator=separator
        self.items.append(RawLatex(f"\\noindent {title} \\\\ \\noindent Due: {due_date}"))
    
class RawLatex:
    def __init__(self, tex):
        self.tex = tex
    
    def texify(self, solutions=False):
        return self.tex
    
   