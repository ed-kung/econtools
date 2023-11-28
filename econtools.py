import os
import numpy as np
import requests
import json

#------------------------------------------------ Text and number manipulation
def prettify(x, scale=(1,'',1,''), numtype='p', fmt='%0.4g', latex=True):
    # numtype can be p, q, pq, pct, or ''

    if x<0:
        pm = '$-$'
    else:
        pm = ''

    if (numtype=='p' or numtype=='pq'):
        dol = '$'
    else:
        dol = ''

    unitlist = ['', 'k', 'm', 'b', 't']
    if (numtype=='p'):
        scal   = scale[2]
        unit   = scale[3]
        unitid = unitlist.index(unit) 
        suffix = ''
    elif (numtype=='q'):
        scal   = scale[0]
        unit   = scale[1]
        unitid = unitlist.index(unit)
        suffix = ''
    elif (numtype=='pq'):
        scal    = scale[0]*scale[2]
        qunit   = scale[1]
        punit   = scale[3]
        qunitid = unitlist.index(qunit)
        punitid = unitlist.index(punit)
        unitid  = punitid + qunitid
        if (unitid>4):
            raise
        unit = unitlist[unitid]
        suffix = ''
    elif (numtype=='pct'):
        scal   = 100
        unit   = ''
        unitid = 0
        suffix = '%'
    else:
        scal   = 1
        unit   = ''
        unitid = 0
        suffix = ''
        
    x      = abs(x*scal*10**(3*unitid))
    unit   = ''
    unitid = 0
    while (x>=1000 and unitid<4):
        x = x/1000
        unitid+=1
        unit = unitlist[unitid]
    xfmt = fmt % x
    
    if (latex):
        output = pm + dol.replace('$','\\$') + xfmt + unit + suffix.replace('%','\\%')
    else:
        output = pm.replace('$','') + dol + xfmt + unit + suffix
    
    return output


class paragraph:
    def __init__(self, text, latex=True):
        self.text  = text
        self.latex = latex

    def print_latex(self, solution=False):
        if (self.latex):
            return self.text + '\n\n'
        else:
            return self.text.replace('$','\\$').replace('%','\\%') + '\n\n'

    def print_html(self):
        if (self.latex):
            return '<p>' + self.text.replace('\\$','$').replace('\\%','%').replace('$-$','-').replace('\\fb','______') + '</p>\n'
        else:
            return '<p>' + self.text + '</p>\n'
    
class question_text:
    def __init__(self, *args):
        self.qt = []
        for arg in args:
            if type(arg)==str:
                self.qt.append(paragraph(arg))
            else:
                self.qt.append(arg)
    def append(self, o):
        if type(o)==str:
            self.qt.append(paragraph(o))
        else:
            self.qt.append(o)
    def print_latex(self, solution=False):
        t=''
        for o in self.qt:
            t+= o.print_latex(solution)
        return t
    def print_html(self):
        t=''
        for o in self.qt:
            t+= o.print_html()
        return t

class equation:
    # Y = a + bX
    def __init__(self, a, b, ylab, xlab, fmt='%0.4g'):
        self.ylab = ylab
        self.xlab = xlab
        self.a    = a
        self.b    = b
        self.fmt  = fmt
    def print_latex(self, solution=False):
        t = '\\begin{align*} \n'
        a = self.fmt % self.a
        b = self.fmt % abs(self.b)
        
        t+= '%s = ' % self.ylab
        if self.a!=0:
            t+= '%s ' % a
        if abs(self.b)==1 and self.b<0:
            t+= '- %s \n' % self.xlab
        elif abs(self.b)==1 and self.b>0:
            t+= '+ %s \n' % self.xlab
        elif self.b<0:
            t+= '- %s%s \n' % (b, self.xlab)
        else:
            t+= '+ %s%s \n' % (b, self.xlab)
            
        t+= '\\end{align*}\n'
        return t

class multieq:
    def __init__(self, *args):
        self.eqlist = []
        for arg in args:
            self.eqlist.append(arg)
    def print_latex(self, solution=False):
        t = '\\begin{align*} \n'
        i=0
        for eq in self.eqlist:
            a = eq.fmt % eq.a
            b = eq.fmt % abs(eq.b)
            t+= '%s &= ' % eq.ylab
            if eq.a!=0:
                t+= '%s ' % a
            if abs(eq.b)==1 and eq.b<0:
                t+= '- %s' % eq.xlab
            elif abs(eq.b)==1 and eq.b>0:
                t+= '+ %s' % eq.xlab
            elif eq.b<0:
                t+= '- %s%s' % (b, eq.xlab)
            elif eq.b>0 and eq.a==0:
                t+= '%s%s' % (b, eq.xlab)
            else:
                t+= '+ %s%s' % (b, eq.xlab)
            i+=1
            if i==len(self.eqlist):
                t+='\n'
            else:
                t+='\\\\ \n'
        t+= '\\end{align*}\n'
        return t

    def add_image(self, img_w, img_h, img_id, img_name, course_id):
        self.img_w     = img_w
        self.img_h     = img_h
        self.img_id    = img_id
        self.img_name  = img_name
        self.course_id = course_id
    
    def print_html(self):
        #return '<p><img src="/courses/%s/files/%s/preview" alt="%s" \
        #        width="%g" height="%g" /></p>\n' % (self.course_id, 
        #        self.img_id, self.img_name, self.img_w, self.img_h)
        t=''
        i=0
        for eq in self.eqlist:
            t+='<p>'
            a = eq.fmt % eq.a
            b = eq.fmt % abs(eq.b)
            t+= '%s = ' % eq.ylab
            if eq.a!=0:
                t+= '%s ' % a
            if abs(eq.b)==1 and eq.b<0:
                t+= '- %s' % eq.xlab
            elif abs(eq.b)==1 and eq.b>0:
                t+= '+ %s' % eq.xlab
            elif eq.b<0:
                t+= '- %s%s' % (b, eq.xlab)
            elif eq.b>0 and eq.a==0:
                t+= '%s%s' % (b, eq.xlab)
            else:
                t+= '+ %s%s' % (b, eq.xlab)
            i+=1
            t+='</p>'
        return t
    


#--------------------------------------------------------------- Graphing tools
class point:
    def __init__(self, x, y, lab='', labpos='right', labsz='small', dotsz='2pt', color='black'):
        self.x      = x
        self.y      = y
        self.labsz  = labsz
        self.lab    = lab
        self.dotsz  = dotsz
        self.labpos = labpos
        self.color  = color
    def print_latex(self, xbounds, ybounds):
        if (self.x >= xbounds[0] and self.x <= xbounds[1] and 
            self.y >= ybounds[0] and self.y <= ybounds[1]):
            t = '\\fill [color=%s] (%g, %g) circle [radius=%s];\n' % \
                (self.color, self.x, self.y, self.dotsz)
            if (len(self.lab)>0):
                t+= '\\draw [color=%s] (%g, %g) node [%s] {\\%s %s};\n' % \
                    (self.color, self.x, self.y, self.labpos, self.labsz, self.lab)
            return t
        else:
            return ''

class line:
    def __init__(self, a, b, name='', lab='', labpos='right', labsz='small', lwidth='0.8pt', 
                 color='black', xmin=0, ymin=0, xmax=999, ymax=999):
        self.a       = float(a)
        self.b       = float(b)
        self.name    = name
        self.lab     = lab
        self.labpos  = labpos
        self.labsz   = labsz
        self.lwidth  = lwidth
        self.color   = color
        self.xmin    = xmin
        self.xmax    = xmax
        self.ymin    = ymin
        self.ymax    = ymax
    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        t = '\\addplot [name path=%s, domain=%g:%g, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {%g + %g*x} \
                        node [%s] {\\%s %s};\n' % \
            (self.name, xmin,xmax, ymin,ymax, self.color, self.lwidth, self.a, self.b, 
             self.labpos, self.labsz, self.lab)
        return t
    def eval(self, x):
        return self.a + self.b*x
    def inveval(self, y):
        return -self.a/self.b + 1/self.b * y

class line_segment:
    def __init__(self, point1, point2, lab='', labpos='right', labsz='small', lwidth='2pt',
                 color='black'):
        self.point1 = point1
        self.point2 = point2
        self.lab = lab
        self.labpos = labpos
        self.labsz = labsz
        self.lwidth = lwidth
        self.color = color
    def print_latex(self, xbounds=0, ybounds=0):
        x1 = self.point1.x
        x2 = self.point2.x
        y1 = self.point1.y
        y2 = self.point2.y
        xmid = (x1+x2)/2
        ymid = (y1+y2)/2
        t = '\\draw [color=%s, line width=%s] (%g,%g)--(%g,%g);\n' % \
            (self.color, self.lwidth, x1, y1, x2, y2)
        t+= '\\draw (%g,%g) node [color=%s, %s] {%s};\n' % \
            (xmid, ymid, self.color, self.labpos, self.lab)
        return t
        
class dropline:
    def __init__(self, point, ylab='', xlab='', labsz='small'):
        self.point = point
        self.ylab = ylab
        self.xlab = xlab
    def print_latex(self, xbounds=0, ybounds=0):
        t = ''
        if self.ylab:
            t+= '\\draw [dotted] (%g,%g)--(0,%g) node [left] {%s};\n' % \
                (self.point.x, self.point.y, self.point.y, self.ylab)
        if self.xlab:
            t+= '\\draw [dotted] (%g,%g)--(%g,0) node [below] {%s};\n' % \
                (self.point.x, self.point.y, self.point.x, self.xlab)
        return t

class parabola:
    def __init__(self, point_min, point2, name='', lab='', labpos='right', labsz='small', 
                 lwidth='0.8pt', color='black', xmin=1, ymin=0, xmax=999, ymax=999):
        x_min = point_min.x
        y_min = point_min.y
        x2   = point2.x
        y2   = point2.y
        VEC  = np.array([y_min, y2, 0]).reshape(3,1)
        MAT  = np.array([[x_min**2, x_min, 1], [x2**2, x2, 1], [2*x_min, 1, 0]])
        SOL  = np.linalg.solve(MAT, VEC)
        self.a = SOL[0]
        self.b = SOL[1]
        self.c = SOL[2]
        self.name    = name
        self.lab     = lab
        self.labpos  = labpos
        self.labsz   = labsz
        self.lwidth  = lwidth
        self.color   = color
        self.xmin    = xmin
        self.xmax    = xmax
        self.ymin    = ymin
        self.ymax    = ymax
        
    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        t = '\\addplot [name path=%s, domain=%g:%g, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {%g*x*x + %g*x + %g} \
                        node [%s] {\\%s %s};\n' % \
            (self.name, xmin,xmax, ymin,ymax, self.color, self.lwidth, 
             self.a, self.b, self.c, self.labpos, self.labsz, self.lab)
        return t
    def eval(self, x):
        return self.a*x**2 + self.b*x + self.c


class indifference_curve:
    # See ces_curves.lyx
    def __init__(self, point, slope, rho, lab='', labpos='right', labsz='small',
                 lwidth='0.8pt', color='black', xmin=1, ymin=1, xmax=99, ymax=99):
        alpha = -pow(point.y,rho-1)*slope/(pow(point.x,rho-1) - pow(point.y,rho-1)*slope)
        U0 = pow(alpha*pow(point.x,rho)+(1-alpha)*pow(point.y,rho), 1/rho)
        self.alpha = alpha
        self.U0 = U0
        self.rho = rho
        self.lab = lab
        self.labpos = labpos
        self.labsz = labsz
        self.lwidth = lwidth
        self.color = color
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        
        t = '\\addplot [domain=%g:%g, samples=1000, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {pow(1/(1-%g), 1/%g)*pow(pow(%g,%g) - %g*pow(x,%g), 1/%g)} \
                        node [%s] {\\%s %s};\n' % (
                        xmin,xmax,ymin,ymax,self.color,self.lwidth,
                        self.alpha,self.rho,self.U0,self.rho,self.alpha,self.rho,self.rho,
                        self.labpos, self.labsz, self.lab
                        )
        return t
    


class arc: 
    def __init__(self, xmax, ymax, xmin=0, ymin=0, lwidth='0.8pt', color='black', name=''):
        # Initialize 
        self.xmax = xmax
        self.ymax = ymax
        self.xmin = xmin
        self.ymin = ymin
        self.lwidth = lwidth
        self.color = color
        self.name = name
    
    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        t = '\\addplot [name path=%s, domain=%g:%g, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {%g * (1 - (x/%g)^2)^0.5};\n' % \
            (self.name, xmin, xmax, ymin, ymax, self.color, self.lwidth, 
             self.ymax, self.xmax)
        return t
        
        

class curve:
    def __init__(self, MC, point, name='', lab='', labpos='right', labsz='small', lwidth='0.8pt',
                 color='black', xmin=1, ymin=0, xmax=999, ymax=999):
        # Initialize with a MC curve (a line) and one other point on the curve
        self.F = (point.y - MC.a)*point.x - 0.5*MC.b*(point.x**2)
        self.a = MC.a
        self.b = MC.b
        self.name = name
        self.lab  = lab
        self.labpos = labpos
        self.labsz = labsz
        self.lwidth = lwidth
        self.color = color
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        t = '\\addplot [name path=%s, domain=%g:%g, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {%g/x + %g + 0.5*%g*x} \
                        node [%s] {\\%s %s};\n' % \
            (self.name, xmin,xmax, ymin,ymax, self.color, self.lwidth, self.F, self.a, self.b, 
             self.labpos, self.labsz, self.lab)
        return t
    
    def eval(self, x):
        return self.F/x + self.a + 0.5*self.b*x
    
    def slope(self, x):
        return -self.F/(x**2) + 0.5*self.b
    
    def inveval(self, y):
        A = 0.5*self.b
        B = self.a - y
        C = self.F
        return -B+np.sqrt(B**2 - 4*A*C)
    
    def minimum(self):
        return np.sqrt(2*self.F / self.b)

class curve2:
    # Initialize with a parabolic MC curve and the efficient scale
    # If efficient_scale=None, gives the AVC curve
    def __init__(self, MC, escale, name='', lab='', labpos='right', labsz='small', lwidth='0.8pt', 
                 color='black', xmin=1, ymin=0, xmax=999, ymax=999):
        if (escale==None):
            self.F = 0
            self.a = MC.a
            self.b = MC.b
            self.c = MC.c
        else:
            self.F = (2.0/3.0)*MC.a*escale**3 + 0.5*MC.b*escale**2 
            self.a = MC.a
            self.b = MC.b
            self.c = MC.c
        self.name = name
        self.lab  = lab
        self.labpos = labpos
        self.labsz = labsz
        self.lwidth = lwidth
        self.color = color
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def print_latex(self, xbounds, ybounds):
        xmin = max(self.xmin, xbounds[0])
        xmax = min(self.xmax, xbounds[1])
        ymin = max(self.ymin, ybounds[0])
        ymax = min(self.ymax, ybounds[1])
        t = '\\addplot [name path=%s, domain=%g:%g, restrict y to domain=%g:%g, \
                        color=%s, line width=%s] {%g/x + %g*x^2 + %g*x + %g} \
                        node [%s] {\\%s %s};\n' % \
            (self.name, xmin,xmax, ymin,ymax, self.color, self.lwidth, 
             self.F, self.a/3, self.b/2, self.c, 
             self.labpos, self.labsz, self.lab)
        return t
    


class axis:
    def __init__(self, 
                 xmax=11, ymax=11, xlab='Q', ylab='P', labsz='small',
                 scale=(1,'',1,''), prefix=('','\\$'), 
                 yfmt='%g', xfmt='%g', grid=True, xrot=True, 
                 width='3.5in', xoffset='0in', yoffset='0in', 
                 subaxis=False, centering=False, title='', titlesz='small', 
                 skip=1):
        self.xmax      = xmax
        self.ymax      = ymax
        self.xlab      = xlab
        self.ylab      = ylab
        self.labsz     = labsz
        self.scale     = scale
        self.prefix    = prefix
        self.yfmt      = yfmt
        self.xfmt      = xfmt
        self.grid      = grid
        self.xrot      = xrot
        self.width     = width
        self.xoffset   = xoffset
        self.yoffset   = yoffset
        self.subaxis   = subaxis
        self.centering = centering
        self.title     = title
        self.titlesz   = titlesz
        self.objlist   = []
        self.solobjlist = []
        self.skip       = skip
        
    def add(self, *args):
        for o in args:
            self.objlist.append(o)
            
    def addsol(self, *args):
        for o in args:
            self.solobjlist.append(o)
            
    def add_image(self, img_w, img_h, img_id, img_name, course_id):
        self.img_w     = img_w
        self.img_h     = img_h
        self.img_id    = img_id
        self.img_name  = img_name
        self.course_id = course_id
        
    def add_alt_text(self, alt_text):
        self.alt_text = alt_text
        
    def print_html(self):
        #return '<p><img src="/courses/%s/files/%s/preview" alt="%s" \
        #        width="%g" height="%g" /></p>\n' % (self.course_id, 
        #        self.img_id, self.img_name, self.img_w, self.img_h)
        return '<p>' + self.alt_text + '</p>'
    
    def print_latex(self, solution=False):
        t=''
        
        if (not self.subaxis):
            if (self.centering):
                t+= '\\begin{center}\n'
            t+= '\\begin{tikzpicture}\n'
        
        t+= '\\begin{axis}[                      \n'
        t+= '   xshift=%s,                       \n' % (self.xoffset)
        t+= '   yshift=%s,                       \n' % (self.yoffset) 
        t+= '   axis lines = middle,             \n' 
        t+= '   xlabel=\\%s %s,                  \n' % (self.labsz, self.xlab)
        t+= '   ylabel=\\%s %s,                  \n' % (self.labsz, self.ylab)
        t+= '   xmin=0,                          \n' 
        t+= '   ymin=0,                          \n'
        t+= '   xmax=%g,                         \n' % (self.xmax)
        t+= '   ymax=%g,                         \n' % (self.ymax)
        t+= '   width=%s,                        \n' % (self.width)
        t+= '   ticks=none,                      \n'
        t+= '   every axis y label/.style = {    \n'
        t+= '      at={(ticklabel* cs:1.00)},    \n'
        t+= '      anchor=south,                 \n'
        t+= '   },                               \n'
        t+= '   every axis x label/.style = {    \n'
        t+= '      at={(ticklabel* cs:1.00)},    \n'
        t+= '      anchor=west,                  \n'
        t+= '   },                               \n'
        t+= '   clip=false                       \n'
        t+= ']\n'
        
        if (self.grid):
            for i in range(1,self.xmax):
                myx   = self.xfmt % (i*self.scale[0])
                if (i%self.skip)==0:
                    mylab = '\\%s %s%s%s' % (self.labsz, self.prefix[0], myx, self.scale[1])
                else:
                    mylab = ''
                if (self.xrot):
                    t+= '\\draw [dotted] (%g,%g)--(%g,%g) node [below right, rotate=-45] {%s};\n' % \
                        (i, self.ymax, i, 0, mylab)
                else:
                    t+= '\\draw [dotted] (%g,%g)--(%g,%g) node [below] {%s};\n' % \
                        (i, self.ymax, i, 0, mylab)
            for i in range(1,self.ymax):
                myy   = self.yfmt % (i*self.scale[2])
                if (i%self.skip)==0:
                    mylab = '\\%s %s%s%s' % (self.labsz, self.prefix[1], myy, self.scale[3])
                else:
                    mylab = ''
                t+= '\\draw [dotted] (%g,%g)--(%g,%g) node [left] {%s};\n' % \
                    (self.xmax, i, 0, i, mylab)
            t+= '\\draw (0,0) node [below left] {\\%s 0};\n' % (self.labsz)
        
        for obj in self.objlist:
            t+= obj.print_latex(xbounds=(0,self.xmax), ybounds=(0,self.ymax))
            
        if (solution):
            for obj in self.solobjlist:
                t+=obj.print_latex(xbounds=(0,self.xmax), ybounds=(0,self.ymax))
        
        t+= '\\draw (%g,%g) node [above] {\\%s %s};\n' % \
            (self.xmax/2, self.ymax, self.titlesz, self.title)
        
        t+= '\\end{axis}\n'
        
        if (not self.subaxis):
            t+= '\\end{tikzpicture}\n'
            if (self.centering):
                t+= '\\end{center}\n'
            t+='\n\n'
        
        return t

class multiaxis:
    def __init__(self, *args, centering=False):
        self.centering = centering
        self.axlist = []
        for o in args:
            self.axlist.append(o)
        for ax in self.axlist:
            ax.subaxis   = True
            ax.centering = False

    def add_image(self, img_w, img_h, img_id, img_name, course_id):
        self.img_w     = img_w
        self.img_h     = img_h
        self.img_id    = img_id
        self.img_name  = img_name
        self.course_id = course_id
        
    def print_html(self):
        #return '<p><img src="/courses/%s/files/%s/preview" alt="%s" \
        #        width="%g" height="%g" /></p>\n' % (self.course_id, 
        #        self.img_id, self.img_name, self.img_w, self.img_h)
        t=''
        for ax in self.axlist:
            t+='<p>'
            t+=ax.print_html()
            t+='</p>'
        return t
    
    def print_latex(self, solution=False):
        t=''
        if (self.centering):
            t+= '\\begin{center}\n'
        t+= '\\begin{tikzpicture}\n'
        for ax in self.axlist:
            t+= ax.print_latex(solution)
        t+= '\\end{tikzpicture}\n'
        if (self.centering):
            t+= '\\end{center}\n'
        t+='\n\n'
        return t
        
def line_that_passes(A, B, name='', lab='', labpos='right', labsz='small', lwidth='0.8pt', 
                 color='black', xmin=0, ymin=0, xmax=999, ymax=999):
    b = (A.y - B.y)/(A.x - B.x)
    a = A.y - b*A.x
    return line(a,b,name,lab,labpos,labsz,lwidth,color,xmin,ymin,xmax,ymax)

def line_intersection(line1, line2, lab='', labpos='right', labsz='small', dotsz='2pt', color='black'):
    x = (line1.a - line2.a)/(line2.b - line1.b)
    y = line1.eval(x)
    return point(x,y,lab,labpos,labsz,dotsz,color)


class normalform:
    def __init__(self, 
                 player_names=['P1','P2'], 
                 strategies=[['Talk','Silent'],['Talk','Silent']], 
                 payoffs=[[['2','2'],['4','1']], 
                          [['1','4'],['3','3']]],
                 best_response=[[0,0],[0,0]], 
                 boxw=5, boxh=3,
                 hide_cells=False, 
				 circle_br_sol=True):
        self.player_names  = player_names
        self.strategies    = strategies
        self.payoffs       = payoffs
        self.best_response = best_response
        self.boxw          = boxw
        self.boxh          = boxh       
        self.hide_cells    = hide_cells
        self.circle_br_sol = circle_br_sol
    
    def print_latex(self, solution=False):
        N = len(self.strategies[0])
        K = len(self.strategies[1])
        boxw = self.boxw
        boxh = self.boxh
        tabw = boxw * K
        tabh = boxh * N
        
        t = '\\begin{tikzpicture}\n'
        
        # Draw player names
        t+= '\\draw (-1, %g) node [above, rotate=90] {%s};\n' % (tabh/2, self.player_names[0])
        t+= '\\draw (%g, %g) node [above] {%s};\n' % (tabw/2, tabh+1, self.player_names[1])
        
        # Draw strategies
        myY = tabh
        for i in range(N):
            t+= '\\draw (-0.2, %g) node [above, rotate=90] {%s};\n' % (myY-boxh/2, self.strategies[0][i])
            myY -= boxh
        myX = 0
        for j in range(K):
            t+= '\\draw (%g, %g) node [above] {%s};\n' % (myX+boxw/2, tabh+0.2, self.strategies[1][j])
            myX += boxw
            
        # Draw cells
        for i in range(N):
            for j in range(K):
                t+='\\node at (%g,%g) [minimum width=%gcm, minimum height=%gcm, \
                                       draw, anchor=north west] {};\n' % \
                    (j*boxw, tabh-i*boxh, boxw, boxh)
                if (not self.hide_cells):
                    t+='\\node at (%g,%g) [minimum width=%gcm, minimum height=%gcm, \
                                           anchor=south west] {\\small %s};\n' % \
                       (j*boxw, tabh-i*boxh-boxh/2, boxw, boxh/2, self.payoffs[i][j][0])
                    t+='\\node at (%g,%g) [minimum width=%gcm, minimum height=%gcm, \
                                           anchor=north west] {\\small %s};\n' % \
                       (j*boxw, tabh-i*boxh-boxh/2, boxw, boxh/2, self.payoffs[i][j][1])
                elif (solution):
                    t+='\\node at (%g,%g) [minimum width=%gcm, minimum height=%gcm, \
                                           anchor=south west] {\\small \\color{red} %s};\n' % \
                       (j*boxw, tabh-i*boxh-boxh/2, boxw, boxh/2, self.payoffs[i][j][0])
                    t+='\\node at (%g,%g) [minimum width=%gcm, minimum height=%gcm, \
                                           anchor=north west] {\\small \\color{red} %s};\n' % \
                       (j*boxw, tabh-i*boxh-boxh/2, boxw, boxh/2, self.payoffs[i][j][1])
                       
        # Circle best responses 
        if (solution and self.circle_br_sol):
            for j in range(K):
                i = self.best_response[0][j]
                t+='\\draw [color=red] (%g,%g) ellipse (%gcm and %gcm);\n' % \
                    (j*boxw+boxw/2, tabh-i*boxh-boxh/4, boxw/2-0.1, boxh/4-0.1)
            for i in range(N):
                j = self.best_response[1][i]
                t+='\\draw [color=red] (%g,%g) ellipse (%gcm and %gcm);\n' % \
                    (j*boxw+boxw/2, tabh-i*boxh-3*boxh/4, boxw/2-0.1, boxh/4-0.1)
        
        t+= '\\end{tikzpicture}\n'
        
        return t
    
    def add_image(self, img_w, img_h, img_id, img_name, course_id):
        self.img_w      = img_w
        self.img_h      = img_h
        self.img_id     = img_id
        self.img_name   = img_name
        self.course_id  = course_id
        
    def print_html(self):
        return '<p><img src="/courses/%s/files/%s/preview" alt="%s" \
                width="%g" height="%g" /></p>\n' % (self.course_id, 
                self.img_id, self.img_name, self.img_w, self.img_h)


class oligopoly:
    def __init__(self, player_names = ['Firm 1','Firm 2'], 
                       player_abbr  = ['F1', 'F2'], 
                       q_choices    = [1,2,3], 
                       q_names      = ['Small','Med','Large'], 
                       demand       = line(10,-1), 
                       atc          = 0, 
                       scale        = (1,'',1,''),
                       boxw=3.5, boxh=2.5, 
                       hide_cells=True,
                       circle_br_sol=True):
        self.player_names  = player_names
        self.player_abbr   = player_abbr
        self.q_choices     = q_choices
        self.q_names       = q_names
        self.demand        = demand
        self.atc           = atc
        self.scale         = scale
        self.boxw          = boxw
        self.boxh          = boxh
        self.hide_cells    = hide_cells
        self.circle_br_sol = circle_br_sol
        
        # Demand schedule table
        Qmin = 2*np.min(q_choices)
        Qmax = 2*np.max(q_choices)
        
        p_row = ['Price']
        q_row = ['Q.Demanded']
        
        for Q in range(Qmin, Qmax+1):
            P = demand.eval(Q)
            p_row.append(prettify(P,scale,numtype='p'))
            q_row.append(prettify(Q,scale,numtype='q'))
        
        tbl_data = [p_row, q_row]
        
        self.demand_tbl = table(tbl_data,coltype='c')
        
        # Strategy names
        strat_names = []
        for i in range(len(q_choices)):
            strat_names.append('%s (%s)' % (q_names[i], prettify(q_choices[i], scale, numtype='q')))
        strategies = [strat_names, strat_names]
        
        # Payoffs
        payoffs = []
        for i in range(len(q_choices)):
            row = []
            for j in range(len(q_choices)):
                q1 = q_choices[i]
                q2 = q_choices[j]
                Q = q1 + q2
                P = demand.eval(Q)
                prof1 = (P-atc)*q1
                prof2 = (P-atc)*q2
                
                col = ['%s profit %s' % (player_abbr[0], prettify(prof1,scale,numtype='pq')), 
                       '%s profit %s' % (player_abbr[1], prettify(prof2,scale,numtype='pq'))]
                
                row.append(col)
            payoffs.append(row)
        
        # Best responses for player 1
        BR1 = []
        for j in range(len(q_choices)):
            br1 = 0
            prof1 = -1000
            for i in range(len(q_choices)):
                q1 = q_choices[i]
                q2 = q_choices[j]
                Q = q1 + q2
                P = demand.eval(Q)
                if ((P-atc)*q1 > prof1):
                    prof1 = (P-atc)*q1
                    br1 = i
            BR1.append(br1)
        
        
        # Best response for player 2
        BR2 = []
        for i in range(len(q_choices)):
            br2 = 0
            prof2 = -1000
            for j in range(len(q_choices)):
                q1 = q_choices[i]
                q2 = q_choices[j]
                Q = q1 + q2
                P = demand.eval(Q)
                if ((P-atc)*q2 > prof2):
                    prof2 = (P-atc)*q2
                    br2 = j
            BR2.append(br2)
        
        best_response = [BR1, BR2]
        
        self.nf = normalform(player_names, strategies, payoffs, best_response,
                             boxw, boxh, hide_cells, circle_br_sol)
    
    
    
#---------------------------------------------------------------------- Tables 
class table:
    def __init__(self, table_data, coltype='C{1in}', show_rows=[0], hide_cols=[]):
        self.table_data = table_data
        self.coltype    = coltype
        self.nrow       = len(table_data)
        self.ncol       = len(table_data[0])
        self.show_rows  = show_rows
        self.hide_cols  = hide_cols
    
    def print_latex(self, solution=False):
        t='\\begin{center}\n'
        t+='\\begin{tabular}{'
        for col in range(self.ncol):
            t+= '|%s' % self.coltype
        t+= '|} \\hline \n'
        
        for row in range(self.nrow):
            for col in range(self.ncol):
                if (not(row in self.show_rows) and (col in self.hide_cols)):
                    if (solution):
                        if (col==0):
                            t+= '{\\color{red} %s}' % self.table_data[row][col]
                        else:
                            t+= '& {\\color{red} %s}' % self.table_data[row][col]
                    else:
                        if (col==0):
                            t+= ' '
                        else:
                            t+='& '
                else:
                    if (col==0):
                        t+= '%s' % self.table_data[row][col]
                    else:
                        t+= '& %s' % self.table_data[row][col]
            t+='\\\\ \\hline \n'
                
        t+= '\\end{tabular}\n'
        t+= '\\end{center}\n'
        return t
            
    def print_html(self):
        t = '<table style="border-collapse: collapse; width: 100%%;" border="1">\n'
        t+= '<tbody>\n'
        for row in range(self.nrow):
            t+= '<tr>\n'
            for col in range(self.ncol):
                mydata = self.table_data[row][col]
                if (type(mydata)==str):
                    mydata = mydata.replace('\\$','$')
                t+= '<td style="width: %g%%; text-align: center;">%s</td>\n' % \
                    (1.0/self.ncol, mydata)
            t+= '</tr>\n'
        t+= '</tbody>\n'
        t+= '</table>\n'
        t+= '<p></p>'
        return t





#---------------------------------------------------------------- Problem types
def check_dups(answers):
    if len(answers)!=len(set(answers)):
        print(answers)
        print('Error: duplicate answers')
        raise
        
class multipart:
    def __init__(self, main_text):
        if type(main_text)==str:
            self.main_text = paragraph(main_text)
        else:
            self.main_text = main_text
        self.probs     = []
        self.nparts    = 0
        self.sub_text  = []
        self.type      = 'multipart'
    def append(self, prob, sub_text=None):
        self.probs.append(prob)
        if type(sub_text)==str:
            self.sub_text.append(paragraph(sub_text))
        else:
            self.sub_text.append(sub_text)
        self.nparts+=1

class prob_numer:
    def __init__(self, question_text, ans, scale=(1,'',1,''), numtype='', 
                 fmt='%g', K=4, delta=1, deltatype='add'):
        if (type(question_text)==str):
            self.question_text = paragraph(question_text)
        else:
            self.question_text = question_text

        self.ans     = ans
        self.scale   = scale        
        self.numtype = numtype
        self.fmt     = fmt
        self.K       = K 
        self.type    = 'numeric'
        
        # create distractors
        if (K>1):
            nless   = np.random.randint(K)
            nmore   = K - nless - 1
            answers = [ans]
            for i in range(nless):
                if deltatype=='add':
                    answers.append(ans - delta*(i+1))
                if deltatype=='mul':
                    answers.append(ans*delta**(-i-1))
                    
            for i in range(nmore):
                if deltatype=='add':
                    answers.append(ans + delta*(i+1))
                if deltatype=='mul':
                    answers.append(ans*delta**(i+1))
        
        # sort answers
        self.answers = answers.copy()
        sortindex = np.argsort(answers)
        for i in range(len(answers)):
            self.answers[i] = answers[sortindex[i]]
        self.solution = sortindex.tolist().index(0)

        # check for duplicates
        check_dups(self.answers)       
        
    def print_latex(self, solution=True):
        # prettify answers
        self.pretty_answers = []
        for i in range(self.K):
            self.pretty_answers.append( prettify(self.answers[i], self.scale, 
                                                 self.numtype, self.fmt, latex=True))
        # check for duplicates
        check_dups(self.pretty_answers)
        
        t=''
        if (self.K>1):
            t+= self.question_text.print_latex(solution)
            for i in range(len(self.pretty_answers)):
                t+= '~ %s) %s\n' % (chr(97+i), self.pretty_answers[i]) 
            if (solution):
                t+= '{\\color{red} Answer: %s} \n' % (chr(97+self.solution))
        return t
    

    def upload(self, url, headers, qnum, position):
        # prettify answers
        self.pretty_answers = []
        for i in range(self.K):
            self.pretty_answers.append( prettify(self.answers[i], self.scale, 
                                                 self.numtype, self.fmt, latex=False))
        # check for duplicates
        check_dups(self.pretty_answers)
        
        answer_data = []
        for j in range(len(self.pretty_answers)):
            if j==self.solution:
                weight=100
            else:
                weight=0
            
            answer_data.append( {
                'answer_text': self.pretty_answers[j], 
                'answer_weight': weight
                })
        
        question_data = {
            'question_name': 'Question %d' % (qnum), 
            'question_text': self.question_text.print_html(), 
            'question_type': 'multiple_choice_question', 
            'points_possible': 1, 
            'position': position, 
            'answers': answer_data
            }
        
        data = {'question': question_data}
        r = requests.post(url=url, headers=headers, json=data)
        print('Uploading question %d: Status %s' % (qnum, r))
        
    

class prob_mpc:
    def __init__(self, question_text, answers, solution=0, 
                 horizontal=False, shuffle=True, sort=False):
        if (type(question_text)==str):
            self.question_text = paragraph(question_text)
        else:
            self.question_text = question_text

        self.answers    = answers
        self.solution   = solution
        self.horizontal = horizontal
        self.type       = 'mpc'
        
        if sort:
            self.answers = answers.copy()
            sortindex = np.argsort(answers)
            for i in range(len(answers)):
                self.answers[i] = answers[sortindex[i]]
            self.solution = sortindex.tolist().index(solution)
        elif shuffle:
            perm = np.random.permutation(len(self.answers))
            tempans = self.answers.copy()
            for i in range(len(self.answers)):
                self.answers[perm[i]] = tempans[i]
            self.solution = perm[self.solution]
        
        check_dups(answers)
    
    def print_latex(self, solution=True):
        t=''
        if self.horizontal:
            t+= self.question_text.print_latex(solution)
            for i in range(len(self.answers)):
                t+= '~ %s) %s\n' % (chr(97+i), self.answers[i])
        else:
            t+= self.question_text.print_latex(solution)
            #t+= self.text + '\\vspace{0.1cm} \n'
            t+= '  \\begin{enumerate}[(a)]\n'
            for i in range(len(self.answers)):
                t+= '    \\item %s \n' % (self.answers[i])
            t+= '  \\end{enumerate}\n'
        if solution:
            t+= '\n{\\color{red} Answer: %s}\n' % (chr(97+self.solution))
        return t


    def upload(self, url, headers, qnum, position):
        answer_data = []
        for j in range(len(self.answers)):
            if j==self.solution:
                weight=100
            else:
                weight=0
            
            answer_data.append( {
                'answer_text': self.answers[j].replace('\\$','$').replace('$-$','-').replace('\\%','%'), 
                'answer_weight': weight
                })
        
        question_data = {
            'question_name': 'Question %d' % (qnum), 
            'question_text': self.question_text.print_html(), 
            'question_type': 'multiple_choice_question', 
            'points_possible': 1, 
            'position': position, 
            'answers': answer_data
            }
        
        data = {'question': question_data}
        r = requests.post(url=url, headers=headers, json=data)
        print('Uploading question %d: Status %s' % (qnum, r))

class prob_check:
    # answers should be a list of lists, each sublist is ['option', T/F]
    def __init__(self, question_text, answers, columns=1):
        if (type(question_text)==str):
            self.question_text = paragraph(question_text)
        else:
            self.question_text = question_text
        
        self.answers = answers
        self.type    = 'check'
        self.columns = columns
    
    def print_latex(self, solution=True):
        t = ''
        t+= self.question_text.print_latex(solution)
        if self.columns==1:
            t+= '\\begin{itemize}\n'
            for row in self.answers:
                if (solution==True and row[1]==True):
                    t+= '\\item [\\CheckedBox] {\\color{red} %s}\n' % row[0]
                else:
                    t+= '\\item [$\\square$] %s \n' % row[0]
            t+='\\end{itemize}\n'
            return t
        else:
            j=0
            for row in self.answers:
                if (solution==True and row[1]==True):
                    t+= '\\CheckedBox {\\color{red} %s} ~ ~ ~' % row[0]
                else:
                    t+= '$\\square$ %s ~ ~ ~' % row[0]
                j+=1
                if (j%self.columns)==0:
                    t+='\\\\ [1ex]'
            return t

class prob_match:
    def __init__(self, question_text, left, right):
        if (type(question_text)==str):
            self.question_text = paragraph(question_text)
        else:
            self.question_text = question_text
            
        self.left  = left
        self.right = right
        self.type  = 'match'
    
    def print_latex(self, solution=True):
        t = ''
        t+= self.question_text.print_latex(solution)
        
        myperm    = np.random.permutation(len(self.right))
        picheight = len(self.left) * 0.5
        t+= '\\begin{center}\n'
        t+= '\\begin{tikzpicture}\n'
        for i in range(len(self.right)):
            j = myperm[i]
            if i==0:
                t+= '\\node (RTEXT%d) [text width=3in] {%s};\n' % (j, self.right[j])
            else:
                k = myperm[i-1]
                t+= '\\node (RTEXT%d) [below=0.25cm of RTEXT%d, text width=3in] {%s};\n' % (j, k, self.right[j])
            t+= '\\node (RDOT%d) [left=0.15cm of RTEXT%d, circle, fill, inner sep=1.5pt] {};\n' % (j,j)
            t+= '\\node (LDOT%d) [left=1in of RDOT%d, circle, fill, inner sep=1.5pt] {};\n' % (i,j)
            t+= '\\node (LTEXT%d) [left=0.15cm of LDOT%d] {%s};\n' % (i,i,self.left[i])
        if solution==True:
            for i in range(len(self.left)):
                t+= '\\draw [red] (LDOT%d)--(RDOT%d);\n' % (i,i)
        t+= '\\end{tikzpicture}\n'
        t+= '\\end{center}\n'
        return t

class prob_free:
    def __init__(self, question_text, answer, free_space='0.25in'):
        if (type(question_text)==str):
            self.question_text = paragraph(question_text)
        else:
            self.question_text = question_text
        self.answer     = answer
        self.free_space = free_space
        self.type       = 'free'
    
    def print_latex(self, solution=True):
        t = ''
        t+= self.question_text.print_latex(solution)
        if (len(self.answer)>0):
            t+= '\\vspace{-0.5\\baselineskip} \\parbox[t][%s][t]{\\dimexpr\\textwidth-\\leftmargin}{\n' % self.free_space
            if (solution==True):
                t+= '{\\color{red} Answer: ' 
                t+= self.answer
                t+= '}\n'
            t+='}\n'
        return t

class prob_fbfree:
    def __init__(self, question_text, answers):
        self.question_text = question_text
        self.answers       = answers
        self.type          = 'fbfree'
        self.nans          = len(self.answers)
    
    def print_latex(self, solution=True):
        mytuple = []
        for i in range(self.nans):
            if (solution):
                mytuple.append('\\underline{\\color{red} %s}' % self.answers[i])
            else:
                mytuple.append('\\fb')
        mytuple = tuple(mytuple)
        t = self.question_text % mytuple
        return t
        
        

#---------------------------------------------------------------- LaTeX tools        
        
default_preamble = '''
\\documentclass[12pt]{article}
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
'''

def upload_spacer(url, headers, text):
    data = {
        'question': {
            'question_name': '', 
            'question_text': text, 
            'question_type': 'text_only_question'
            }
        }
    r = requests.post(url=url, headers=headers, json=data)
    print('Uploading spacer text: Status %s' % r)


class quiz:
    def __init__(self, coursename='Econ 160', term='Spring 2021', 
                 instructor='Prof. Kung', quizname='Quiz', time='75 minutes',
                 version=1):        
        self.coursename = coursename
        self.term       = term
        self.instructor = instructor
        self.quizname   = quizname
        self.time       = time
        self.version    = version
        self.probs      = []
        self.nprob      = 0
        
    def append(self, prob):
        self.probs.append(prob)
        if (prob.type=='multipart'):
            self.nprob += prob.nparts
        else:
            self.nprob += 1
    
    def print_pdf(self, filename, output_dir, solution=True):
        if (solution):
            filename += '_solutions'
        
        t = default_preamble
        t+= '\\begin{document}\n\n'
        
        if (len(self.coursename) + len(self.term) > 0):
            t+= '%s %s \\\\ \n' % (self.coursename, self.term)
        if (self.version):
            t+= 'Version %u' % (self.version)
        if (len(self.instructor)>0):
            t+= 'Instructor: %s \\\\ \n' % (self.instructor)
        if (len(self.quizname)>0):
            t+= '%s ' % (self.quizname)
        if (solution):
            t+= 'Solutions'
        t+= ' \\\\ \n'
        
        if (len(self.time)>0):
            t+= 'Time: %s \\\\ \n' % (self.time)
        t+= '%d questions \\\\ \n\n\n' % (self.nprob)

        i=1
        for prob in self.probs:
            t+= '\\begin{minipage}{\\textwidth}\n'
            
            if (prob.type=='multipart'):
                t+= 'Questions %d to %d go together.\n\n' % (i, i+prob.nparts-1)
                t+= prob.main_text.print_latex(solution)
                i+= prob.nparts
                for j in range(prob.nparts):
                    if (prob.sub_text[j]!=None):
                        t+= prob.sub_text[j].print_latex(solution)
                    t+= '\\begin{q}\n'
                    t+= prob.probs[j].print_latex(solution)
                    t+= '\\end{q}\n\n'
            else:
                i+= 1
                t+= '\\begin{q}\n'
                t+= prob.print_latex(solution)
                t+= '\\end{q}\n\n'
            
            t+= '\\end{minipage}\n\n ~ \n\n'
            t+= '\\hrule\n\n'
                
        t+= '\\end{document}\n\n'
        
        ofile = open('%s/%s.tex' % (output_dir, filename), 'w')
        ofile.write(t)
        ofile.close()
        os.chdir(output_dir)
        os.system('pdflatex %s' % filename)
        
    def upload(self, course_id, quiz_id, token, honesty_statement=True):
        headers = {
            'Authorization': 'Bearer ' + token, 
            'Accept': 'application/json', 
            'Content-Type': 'application/json'
            }
        url = 'https://canvas.csun.edu/api/v1/courses/%s/quizzes/%s/questions' % (course_id, quiz_id)
        
        if (honesty_statement):
            t = '<p>For this exam I certify that I will not give or receive any assistance, nor have I given or received any assistance, from persons other than myself, for questions related to this exam. I certify that the answers I submit are the result of my own work and no one else\'s.</p>\n <p>I understand that acts of academic dishonesty will be penalized to the full extent allowed by the CSUN code of conduct, including receiving a failing grade for the course.</p>\n <p>By continuing with the exam, I certify that the above statemetns are true and I agree with those statements.</p>'
            upload_spacer(url,headers,t)
        
        i=1
        for prob in self.probs:
            if (prob.type=='multipart'):
                t = '<p>Questions %d to %d go together.</p>\n' % (i, i+prob.nparts-1)
                t+= prob.main_text.print_html()
                upload_spacer(url,headers,t)
                
                for j in range(prob.nparts):
                    if (prob.sub_text[j]!=None):
                        t = prob.sub_text.print_html()
                        upload_spacer(url, headers, t)
                    prob.probs[j].upload(url,headers,i,i)
                    i+=1
            else:
                prob.upload(url,headers,i,i)
                i+=1

class worksheet:
    def __init__(self, name=''):
        self.name  = name
        self.probs = []
        self.nprob = 0
    
    def append(self, prob):
        self.probs.append(prob)
        self.nprob += 1
    
    def print_pdf(self, filename, output_dir, solution=False):
        t = default_preamble
        t+= '\\begin{document}\n\n'
        t+= '%s \n\n~\n\n' % self.name
        
        for prob in self.probs:
            t+= '\\begin{minipage}{\\textwidth}\n'
            t+= '\\begin{q}\n'
            if (prob.type=='multipart'):
                t+= prob.main_text.print_latex(solution)
                t+= '\\begin{enumerate}[(i)]\n'
                for j in range(prob.nparts):
                    if (prob.sub_text[j]!=None):
                        t+='\\end{enumerate}\n'
                        t+= prob.sub_text[j].print_latex(solution)
                        t+='\\begin{enumerate}[(i), resume]\n'
                    t+='\\item '
                    t+=prob.probs[j].print_latex(solution)
                t+='\\end{enumerate}\n'
            else:
                t+=prob.print_latex(solution)
            t+='\\end{q}\n'
            t+='\\end{minipage}\n\n ~ \n\n'
        t+='\\end{document}\n\n'
        
        ofile = open('%s/%s.tex' % (output_dir, filename), 'w')
        ofile.write(t)
        ofile.close()
        os.chdir(output_dir)
        os.system('pdflatex %s' % filename)
        
    

class doc:
    def __init__(self):
        self.latex = []

    def add_latex(self, tex):
        self.latex.append(tex)

    def print_pdf(self, filename, output_dir):
        t = default_preamble
        t+= '\\begin{document}\n\n'
        for tex in self.latex:
            t+= tex
        t+= '\\end{document}\n\n'
        
        ofile = open('%s/%s.tex' % (output_dir, filename), 'w')
        ofile.write(t)
        ofile.close()
        os.chdir(output_dir)
        os.system('pdflatex %s' % filename)


#-------------------------------------------------------------------- Bundles

class generic_cost_curves:
    def __init__(self, point_MCmin=point(2,2), point_ATCmin=point(6,6), 
                 xmax=11, ymax=11, xlab='Q', ylab='\\$', labsz='small', 
                 scale=(1,'',1,''), prefix=('','\\$'), 
                 yfmt='%g', xfmt='%g', grid=False, xrot=True, 
                 width='3.5in', xoffset='0in', yoffset='0in', 
                 subaxis=False, centering=False, title='', titlesz='small'):
        self.ax = axis(xmax,ymax,xlab,ylab,labsz,scale,prefix,yfmt,xfmt,
                       grid,xrot,width,xoffset,yoffset,subaxis,centering,title,titlesz)
        




           
