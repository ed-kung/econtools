class Table:
    def __init__(self, table_data, coltype=r"C{1in}", masked = []):
        self.table_data = table_data      # contains the table data
        self.coltype = coltype            # column signature
        self.nrow = len(table_data)       # number of rows
        self.ncol = len(table_data[0])    # number of columns
        self.masked = masked              # list of tuples of (row, col) to mask
    
    def texify(self, solutions=False):
        t = "\\begin{center}\n"
        t+= "\\begin{tabular}{"
        for col in range(self.ncol):
            t+= f"|{self.coltype}"
        t+= "|} \\hline \n"
        for row in range(self.nrow):
            for col in range(self.ncol):
                entry = self.table_data[row][col]
                if (col > 0):
                    t+= " & "
                if (not solutions) and ((row, col) in self.masked):
                    t+= "??"
                elif (solutions) and ((row, col) in self.masked):
                    t+= f"{{\\color{{red}} {entry} }}"
                else:
                    t+= entry
            t+= " \\\\ \\hline \n"
        t+= "\\end{tabular}\n"
        t+= "\\end{center}\n"
        return t

    def htmlify(self, solutions=False):
        t = '<table border=1px align="center">\n'
        for row in range(self.nrow):
            t+= "<tr>"
            for col in range(self.ncol):
                entry = self.table_data[row][col]
                if (not solutions) and ((row, col) in self.masked):
                    cell = "??"
                elif (solutions) and ((row, col) in self.masked):
                    cell = f'<span style="color:red">{entry}</span>'
                else:
                    cell = entry
                t+= f"<td>{cell}</td>"
            t+= "</tr>\n"
        t+= "</table>"
        return t
                    

