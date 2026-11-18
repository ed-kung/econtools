import numpy as np

class Point:
    def __init__(self, x, y, color='black',text=None, position=None):
        self.x, self.y = x, y
        self.color = color
        self.text = text
        self.position = position
    def plot(self, ax, xg):
        x, y = self.x, self.y
        ax.plot(x,y,'o',color=self.color,markersize=12,label='_nolegend_')
        if self.text is not None:
            shift = xg[2]-xg[0]
            text_x = x
            text_y = y
            horizontalalignment = 'center'
            verticalalignment = 'center'
            if self.position=='sw':
                text_x = text_x - shift
                text_y = text_y - shift
                horizontalalignment = 'right'
                verticalalignment = 'top'
            elif self.position=='ne':
                text_x = text_x + shift
                text_y = text_y + shift
                horizontalalignment = 'left'
                verticalalignment = 'bottom'
            ax.text(text_x, text_y, self.text, color=self.color, horizontalalignment=horizontalalignment, verticalalignment=verticalalignment)
        return ax

class Line:
    # y = mx + b
    # x = (y-b)/m
    def __init__(self, m, b, linewidth=1, color='black', label='_nolegend_', linestyle='solid'):
        self.m, self.b = m, b
        self.linewidth = linewidth
        self.color = color
        self.label = label
        self.linestyle = linestyle
    def plot(self, ax, xg, labelstyle='legend'):
        if labelstyle == 'legend':
            return ax.plot(xg, self.m*xg + self.b, color=self.color, linewidth=self.linewidth, label=self.label, linestyle=self.linestyle)
        elif labelstyle == 'label':
            plotted = ax.plot(xg, self.m*xg + self.b, color=self.color, linewidth=self.linewidth, label='_nolegend_', linestyle=self.linestyle)
            x_end = max(xg)
            y_end = self.eval_at_x(x_end)
            shift = abs(xg[2] - xg[0]) if len(xg) > 2 else 0
            if self.label not in (None, '_nolegend_'):
                ax.text(x_end + shift, y_end, self.label, color=self.color, horizontalalignment='left', verticalalignment='center')
            return plotted
        else:
            raise ValueError("labelstyle must be 'legend' or 'label'")
    def eval_at_x(self, x):
        return self.m*x + self.b
    def eval_at_y(self, y):
        return (y-self.b)/self.m

