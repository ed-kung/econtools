import os
from documents import Homework, RawLatex

doc = Homework(
    title = r"Week 1 Homework",
    due_date = r"Tuesday 9/1 \vspace{1cm}"
)

doc.add(RawLatex(r"""
\begin{q} 
Supply and demand are given by the following equations: 
\begin{align*}
q_d &= 120 - p \\
q_s &= 2p - 30 
\end{align*}
Calculate the equilibrium price and quantity in this market.
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
Supply and demand are given by:
\begin{align*}
q_d &= 120p^{-1/3} \\
q_s &= 60p^{2/3} 
\end{align*}
Calculate the equilibrium price and quantity.
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
Solve the following equation for $x$:
\begin{align*}
4x^{-3} &= 256
\end{align*}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
Simplify:
\begin{align*}
\frac{4x^{1/3}y^{-2/3}}{12x^{-2/3}y^{1/3}}
\end{align*}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
Write $y$ as a function of $x$:
\begin{align*}
8x^{3/4} y^{1/4} = 16
\end{align*}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
If $\ln y - \ln x = -0.05$, then $y$ is larger or smaller than $x$ by how many percent?
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
$f(x) = 10 + 24x - x^2$
\begin{enumerate}[a.]
\item Write down the first derivative, $f^\prime(x)$. 
\item What choice of $x$ maximizes $f(x)$? What is the maximum of $f(x)$?
\end{enumerate}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
$f(x) = 12x^{1/2} - 3x$
\begin{enumerate}[a.]
\item Write down the first derivative, $f^\prime(x)$. 
\item What choice of $x$ maximizes $f(x)$? What is the maximum of $f(x)$?
\end{enumerate}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
A firm is deciding how much output to produce, $q$. It can sell its output at a price of $p=14$. The firm's cost function is:
\begin{align*}
c(q) = 2q + \tfrac{1}{4}q^2
\end{align*}
\begin{enumerate}[a.]
\item Write down the firm's profit function in terms of $q$ and write down the first derivative.
\item What choice of $q$ maximizes the firm's profit? What is the maximum attainable profit?
\end{enumerate}
\end{q}
"""))

doc.add(RawLatex(r"""
\begin{q}
A firm is deciding how much output to produce, $q$. It can sell its output at a price of $p$. The firm's cost function is:
\begin{align*}
c(q) = a + bq + cq^2
\end{align*}
\begin{enumerate}[a.]
\item Write down the firm's profit function in terms of $p$, $q$, $a$, $b$, and $c$. Find the first derivative of the profit function.
\item What choice of $q$ maximizes the firm's profit? Write the answer in terms of $p$, $a$, $b$, and $c$.
\item What is the maximum attainable profit? Write the answer in terms of $a$, $b$, and $c$.
\end{enumerate}
\end{q}
"""))



doc.print_pdf("test", os.path.dirname(os.path.abspath(__file__)))

