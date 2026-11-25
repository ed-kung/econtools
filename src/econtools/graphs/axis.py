import numpy as np
from matplotlib import pyplot as plt
from econtools.math.scaled import Scaled, _check_numtype

class Axis:
    def __init__(self, xn=13, yn=13, xscale=1, yscale=1, xlab=r'$q$', ylab=r'$p$', xnumtype='', ynumtype='$', xrot=0, yrot=0, noticklabels=False, nogridlines=False, title=None):
        self.xn = xn                      # number of grid points on x axis
        self.yn = yn                      # number of grid points on y axis
        self.xscale = xscale              # scale factor of x axis (how many units per grid point)
        self.yscale = yscale              # scale factor of y axis (how many units per grid point)
        self.xlab = xlab                  # label of x axis
        self.ylab = ylab                  # label of y axis
        _check_numtype(xnumtype)
        _check_numtype(ynumtype)
        self.xnumtype = xnumtype          # numtype of x tick labels: '' (plain), '$' (dollars), or '%' (percentage)
        self.ynumtype = ynumtype          # numtype of y tick labels: '' (plain), '$' (dollars), or '%' (percentage)
        self.xrot = xrot                  # rotation angle of x axis labels
        self.yrot = yrot                  # rotation angle of y axis labels
        self.noticklabels = noticklabels  # whether to hide tick labels (default false)
        self.nogridlines = nogridlines    # whether to hide grid lines (default false)
        self.title = title                # title of the graph (default none)
        self.xmax = xn*xscale
        self.ymax = yn*yscale
        self.objects = []
    def add(self, *args):
        # add objects to the axis
        for obj in args:
            self.objects.append(obj)
    def get_figax(self, alpha=0.6, saveas=None):
        fig, ax = plt.subplots()
        ax.set_xticks(np.arange(0, self.xmax, self.xscale))
        ax.set_yticks(np.arange(0, self.ymax, self.yscale))
        if self.noticklabels:
            ax.set_xticklabels([])
            ax.set_yticklabels([])
        else:
            # tick i is worth i*scale; str(Scaled) formats it via format_number -> _human (k/m/B/T, $, %)
            ax.set_xticklabels([str(Scaled(i, self.xscale, self.xnumtype)) for i in range(len(ax.get_xticks()))])
            ax.set_yticklabels([str(Scaled(i, self.yscale, self.ynumtype)) for i in range(len(ax.get_yticks()))])
        ax.set_xlim([0, self.xmax])
        ax.set_ylim([0, self.ymax])
        ax.set_xlabel(self.xlab)
        ax.set_ylabel(self.ylab)
        ax.set_axisbelow(True)
        if not self.nogridlines:
            ax.grid(alpha=alpha)
        if self.title is not None:
            ax.set_title(self.title)
        if saveas is not None:
            plt.savefig(saveas, bbox_inches='tight')
        return fig, ax
    def draw(self, alpha=0.6, legend=None, saveas=None, labelstyle='legend'):
        # labelstyle: 'legend' puts line labels in the legend, 'label' writes them at the end of each line
        fig, ax = self.get_figax(alpha=alpha)
        xg = np.arange(0, self.xmax + self.xscale/20, self.xscale/10)
        for obj in self.objects:
            obj.plot(ax, xg, labelstyle=labelstyle)
        if legend:
            ax.legend()
        if saveas is not None:
            plt.savefig(saveas, bbox_inches='tight')
        return fig, ax

