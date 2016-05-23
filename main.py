import tkinter,tkinter.filedialog,SudokuSolver

class MainWindow(SudokuSolver.GameWindow):
   def __init__(self, parent=None):
      SudokuSolver.GameWindow.__init__(self, parent)
      self.menuBar = tkinter.Menu(self)
      
      self.fileMenu = tkinter.Menu(self.menuBar, tearoff=0)
      self.fileMenu.add_command(label="Open", command = self.loadFromFile)
      self.menuBar.add_cascade(label="File", menu=self.fileMenu)
      
      self.gameMenu = tkinter.Menu(self.menuBar, tearoff=0)
      self.gameMenu.add_command(label="Solve", command = self.solve)
      self.gameMenu.add_command(label="Reset", command = lambda: self.load(SudokuSolver.Board()))
      self.menuBar.add_cascade(label="Game", menu=self.gameMenu)

      self.config(menu=self.menuBar)
   def loadFromFile(self):
      f = tkinter.filedialog.askopenfile(filetypes=[("All Files", "*"), ("CSV", "*.csv"), ("SDK", "*.sdk"), ("Text", "*.txt")])
      if f == None:
         return
      if f.name.split(".")[-1].lower() == "sdk":
         found = False
         for s in (x.strip().lower() for x in f):
            if s == "[puzzle]":
               found = True
               break
         if not found:
            f.seek(0)
      a = []
      for s in (x.strip().split("#")[0] for x in f):
         if len(s) == 0:
            continue
         if len(s) == 9:
            a.append(s)
         else:
            t = s.split(" ")
            if len(t) == 9:
               a.append(t)
            else:
               t = s.split(",")
               if len(t) == 9:
                  a.append(t)
               else:
                  break
         if len(a) == 9:
            break
      if len(a) != 9:
         self.setText("Error")
         return
      b = SudokuSolver.Board()
      for c, s in ([b.cells[x][y], a[x][y]] for x in range(9) for y in range(9)):
         if not s.isdigit():
            continue
         c.forceSetValue(int(s))
      self.load(b)

if __name__ == "__main__":
   MainWindow().mainloop()
