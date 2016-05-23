import itertools,tkinter

class Board:
   def __init__(self):
      self.cells = [[Cell() for x in range(9)] for y in range(9)]
      self.groups = []
      for i in range(9):
         self.groups.append(CellGroup(self.cells[i]))
      for i in range(9):
         self.groups.append(CellGroup([self.cells[j][i] for j in range(9)]))
      for i, j in ([x, y] for x in range(0, 9, 3) for y in range(0, 9, 3)):
         self.groups.append(CellGroup([self.cells[x][y] for x in range(i, i+3) for y in range(j, j+3)]))
   def __iter__(self):
      return (self.cells[x][y] for x in range(9) for y in range(9))
   def reset(self):
      for c in (y for x in self.cells for y in x):
         c.reset()
   def hasErrors(self):
      for i in self.groups:
         if i.hasErrors():
            return True
      return False
   def isComplete(self):
      for c in self:
         if not c.isFound():
            return False
      return True
   def solve(self):
      if self.hasErrors():
         return False
      try:
         for c in (y for x in self.cells for y in x):
            c.cleanGroups()
      except BaseException as e:
         print(str(e))
         return False
      if self.hasErrors():
         return False
      return True

class Cell:
   def __init__(self):
      self.values = [x for x in range(1,10)]
      self.groups = []
      self.changeCallback = lambda: None
      self.foundCallback = lambda: None
   def isFound(self):
      return self.nOptions() == 1
   def nOptions(self):
      return len(self.values)
   def setValue(self, v):
      if self.isFound() or not v in self.values:
         return
      self.values = [v]
      self.changeCallback()
      self.foundCallback()
      self.cleanGroups()
   def forceSetValue(self, v):
      if v<1 or v>9:
         return
      self.values = [v]
      self.changeCallback()
      self.foundCallback()
   def delValue(self, v):
      if self.isFound() or not v in self.values:
         return
      self.values.remove(v)
      self.changeCallback()
      if self.isFound():
         self.foundCallback()
      self.cleanGroups()
   def cleanGroups(self):
      if self.isFound():
         for g in self.groups:
            g.delValue(self.values[0])
      else:
         for n in range(self.nOptions(), 9):
            for g in self.groups:
               if n >= 9-g.nCompleteCells():
                  continue
               for cs in (x for x in itertools.combinations(g.cells,n) if self in x and not any((y.isFound() for y in x))):
                  s = {y for x in cs for y in x.values}
                  if len(s)==n:
                     for c,v in ([x,y] for x in g.cells if not x in cs for y in s):
                        c.delValue(v)
   def reset(self):
      self.values = [x for x in range(1,10)]
      self.changeCallback()
   def toString(self):
      if self.isFound():
         return str(self.values[0])
      if len(self.values)<=3:
         return ", ".join((str(x) for x in self.values))
      return ""

class CellGroup:
   def __init__(self, cells):
      self.cells = cells
      for i in cells:
         i.groups.append(self)
   def nCompleteCells(self):
      return len([0 for x in self.cells if x.isFound()])
   def delValue(self, v):
      for i in self.cells:
         i.delValue(v)
   def hasErrors(self):
      for i, j in itertools.combinations(self.cells, 2):
         if i.isFound() and j.isFound() and i.values[0]==j.values[0]:
            return True
      return False

class GameWindow(tkinter.Tk):
   def __init__(self, parent=None, board=None):
      tkinter.Tk.__init__(self, parent)
      self.title("Sudoku Solver")
      self.parent = parent
      self.boardGroup = tkinter.Frame(self, background="black")
      self.buttonGroups = [[tkinter.Frame(self.boardGroup) for x in range(3)] for y in range(3)]
      self.buttons = [[tkinter.Button(self, width=5, height=3, borderwidth=1) for x in range(9)] for y in range(9)]
      self.textField = tkinter.Label(self)
      self.grid()
      self.boardGroup.grid(row=0, column=0)
      for bg, i, j in ([self.buttonGroups[x][y], x, y] for x in range(3) for y in range(3)):
         bg.grid(column=i, row=j, padx=i%2, pady=j%2)
      for b, i, j in ([self.buttons[x][y], x, y] for x in range(9) for y in range(9)):
         b.grid(in_=self.buttonGroups[i//3][j//3],column=i%3, row=j%3)
         b.bind("<Button-1>", lambda event, i=i, j=j: self.onCellClick(i, j))
         b.bind("<Button-3>", lambda event, i=i, j=j: self.onCellRightClick(i, j))
      self.textField.grid(row=1, column=0)
      self.resizable(False, False)
      self.bind("<Key>", lambda event: self.onKeyPress(event.char))
      self.bind("<Return>", lambda event: self.solve())
      self.bind("<space>", lambda event: self.animationOff())
      self.bind("<Escape>", lambda event: self.destroy())
      if board==None:
         self.load(Board())
      else:
         self.load(board)
   def load(self, board):
      self.board = board
      self.selectedCell = None
      self.selectedButton = None
      self.textField.config(text="")
      self.animationOff()
      for b, c in ([self.buttons[x][y], self.board.cells[x][y]] for x in range(9) for y in range(9)):
         c.changeCallback = lambda b=b, c=c: b.config(text=c.toString())
         c.changeCallback()
   def onCellClick(self, row, column):
      self.selectedCell = self.board.cells[row][column]
      self.selectedButton = self.buttons[row][column]
      self.setText(", ".join((str(x) for x in self.selectedCell.values)))
   def onCellRightClick(self, row, column):
      self.selectedCell = self.board.cells[row][column]
      self.selectedButton = self.buttons[row][column]
      self.selectedCell.reset()
      self.setText(", ".join((str(x) for x in self.selectedCell.values)))
   def onKeyPress(self, key):
      if not key.isdigit() or key=="0" or self.selectedCell==None:
         return
      self.selectedCell.forceSetValue(int(key))
      self.setText(", ".join((str(x) for x in self.selectedCell.values)))
   def onFound(self):
      self.update()
      self.after(150)
   def animationOn(self):
      for c in self.board:
         c.foundCallback = lambda: self.onFound()
   def animationOff(self):
      for c in self.board:
         c.foundCallback = lambda: None
   def setText(self, text):
      self.textField.config(text=str(text))
   def solve(self):
      self.setText("Working...")
      self.animationOn()
      if self.board.solve():
         self.setText("Done!")
      else:
         self.setText("Error")

if __name__ == "__main__":
   GameWindow().mainloop()
