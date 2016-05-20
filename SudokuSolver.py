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
   def reset(self):
      for c in (y for x in self.cells for y in x):
         c.reset()
   def check(self):
      for i in self.groups:
         if not i.check():
            return False
      return True
   def solve(self):
      if not self.check():
         return False
      for c in (y for x in self.cells for y in x):
         c.cleanGroups()
      if not self.check():
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
   def check(self):
      for i, j in ([self.cells[x], self.cells[y]] for x in range(8) for y in range(x+1,9)):
         if i.isFound() and j.isFound() and i.values[0]==j.values[0]:
            return False
      return True

class GameWindow(tkinter.Tk):
   def __init__(self, parent=None, board=None):
      tkinter.Tk.__init__(self, parent)
      self.parent = parent
      if board==None:
         self.init(Board())
      else:
         self.init(board)
      
   def init(self, board):
      self.board = board
      self.selectedCell = None
      self.selectedButton = None
      self.boardGroup = tkinter.Frame(self, background="gray")
      self.buttonGroups = [[tkinter.Frame(self.boardGroup) for x in range(3)] for y in range(3)]
      self.buttons = [[tkinter.Button(self, width=5, height=3, borderwidth=2) for x in range(9)] for y in range(9)]
      self.textField = tkinter.Label(self)
      
      self.bind("<Key>", lambda event: self.onKeyPress(event.char))
      self.bind("<Return>", lambda event: self.onReturnPress())
      self.bind("<space>", lambda event: self.onSpacePress())
      self.bind("<Escape>", lambda event: self.destroy())
      
      self.grid()
      self.boardGroup.grid(row=0, column=0)
      for bg, i, j in ([self.buttonGroups[x][y], x, y] for x in range(3) for y in range(3)):
         bg.grid(column=i, row=j, padx=1, pady=1)
      for b, c, i, j in ([self.buttons[x][y], self.board.cells[x][y], x, y] for x in range(9) for y in range(9)):
         b.grid(in_=self.buttonGroups[i//3][j//3],column=i%3, row=j%3)
         b.bind("<Button-1>", lambda event, i=i, j=j: self.onCellClick(i, j))
         b.bind("<Button-3>", lambda event, i=i, j=j: self.onCellRightClick(i, j))
         c.changeCallback = lambda b=b, c=c: b.config(text=c.toString())
      self.textField.grid(row=1, column=0)
      self.resizable(False, False)
   def onCellClick(self, row, column):
      self.selectedCell = self.board.cells[row][column]
      self.selectedButton = self.buttons[row][column]
      self.textField.config(text=str(self.selectedCell.values))
   def onCellRightClick(self, row, column):
      self.selectedCell = self.board.cells[row][column]
      self.selectedButton = self.buttons[row][column]
      self.selectedCell.reset()
      self.textField.config(text=str(self.selectedCell.values))
   def onKeyPress(self, key):
      if not key.isdigit() or key=="0" or self.selectedCell==None:
         return
      self.selectedCell.forceSetValue(int(key))
      self.textField.config(text=str(self.selectedCell.values))
   def onReturnPress(self):
      self.textField.config(text="Working...")
      for c in (self.board.cells[x][y] for x in range(9) for y in range(9)):
         c.foundCallback = lambda: self.onFound()
      if self.board.solve():
         self.textField.config(text="Done!")
      else:
         self.textField.config(text="Error")
   def onSpacePress(self):
      for c in (self.board.cells[x][y] for x in range(9) for y in range(9)):
         c.foundCallback = lambda: None
   def onFound(self):
      self.update()
      self.after(150)

if __name__ == "__main__":
   GameWindow().mainloop()
