from tkinter import *
from tkinter import messagebox
import random


class Tile(Label):
    ''' Tile() -> Class for a tile of Minesweeper'''

    def __init__(self, master, coord, isbomb):
        '''Tile.__init__(master,row,column) -> creates tile at a location'''
        Label.__init__(self, master, height=1, width=2, text='', bg='light gray', font=('Ariel', 12))
        self['relief'] = GROOVE
        self.coord = coord  # tuple of location (row,column)\
        self.isbomb = isbomb  # whether tile contains a bomb
        self.number = 0  # default
        self.flag = False  # whether flag is placed on tile
        self.leftClicked = False

        self.bind('<Button-1>', self.left_click)
        self.bind('<Button-3>', self.flag_tile)

    def get_number(self):
        '''Tile.get_number() -> int
        returns tile number'''
        return self.number

    def get_coord(self):
        '''Tile.get_coord() -> tuple
        returns coordinate of tile'''
        return self.coord

    def get_flag(self):
        '''Tile.get_flag() -> boolean
        returns whether tile has been flagged'''
        return self.flag

    def get_isbomb(self):
        '''Tile.get_isbomb() -> boolean
        returns whether tile has a bomb'''
        return self.isbomb

    def left_click(self, event):
        '''Tile.change_num(event)
        changes self.number of tile if self.isbomb == False
        otherwise game over'''
        self.leftClicked = True
        self.update_display()

    def flag_tile(self, event):
        '''Tile.flag_tile(event)
        sets self.flag to True if currently False
        sets self.flag to False if currently True'''
        if self.flag:
            self.flag = False
            self.master.numFlag -= 1
        else:
            self.flag = True
            self.master.numFlag += 1
        self.update_display()
        self.master.update_display()

    def update_display(self):
        '''Tile.update_display()
        shows number of tile if clicked, flag, or bomb'''
        if self.leftClicked and not self.flag: # cannot be flag
            self.master.numTilesClicked += 1
            self['relief'] = SUNKEN
            colormap = ['', 'blue', 'darkgreen', 'red', 'purple', 'maroon', 'cyan', 'black', 'dim gray']
            if not self.isbomb:
                self.number = self.master.find_number(self)  # number of bombs nearby
                if self.number == 0:
                    self['text'] = ''
                    self.master.auto_click(self) # clickes tiles nearby
                else:
                    self['fg'] = colormap[self.number]
                    self['text'] = str(self.number)
                if self.master.numTilesClicked == self.master.limit:
                    self.master.win()

            else: # if bomb
                self.master.lost()
        if self.flag and self['relief'] == GROOVE: # if self.flag is true and has not been clicked
            self['text'] = '*'
        elif not self.flag and self['relief'] == GROOVE: # if self.flag is false and has not been clicked
            self['text'] = ''


class Game(Frame):
    ''' Game() -> Class for the game'''

    def __init__(self, master, width, height, numBombs):
        '''__init__(self,master,width,height,numBombs)
        creates grid of tiles
        sets bombs
        sets tile numbers'''
        Frame.__init__(self, master,bg='white')
        self.grid()
        self.height = height # number of rows of tiles
        self.width = width # number of columns of tiles
        self.numBombs = numBombs
        self.numTilesClicked = 0  # number of clicked tiles
        self.limit = width * height - numBombs  # number of clicked tiles needed to win
        self.bombCoord = []  # list of tuples of bomb coordinates
        self.tiles = {} #dictionary with coordinate of tile paired with object
        self.stopGame = False # ends game when true
        self.numFlag = 0 #number of flagged tiles
        i = 0
        while i < numBombs: # creates random bombs use while loop so there are no duplicates
            bombRow = random.randint(0, self.height-1)
            bombColumn = random.randint(0, self.width-1)
            bombCoordinate = (bombRow,bombColumn) # random coordinate of bomb
            if bombCoordinate not in self.bombCoord: # checks for duplicates
                self.bombCoord.append(bombCoordinate)
                i += 1

        for row in range(height): # creates tiles on grid
            for column in range(width):
                coord = (row,column)
                if coord in self.bombCoord: # if coordinate is a bomb coordinate, make isbomb True
                    self.tiles[coord] = Tile(self,coord,True)
                else:
                    self.tiles[coord] = Tile(self,coord,False)
                self.tiles[coord].grid(row=row,column=column) # adds object to dictionary
        self.counterLabel = Label(self,text = str(self.numBombs-self.numFlag),font = ('Ariel',12))
        self.counterLabel.grid(row = self.height, column = int(self.width/2))

    def auto_click(self, other):
        '''Game.auto_click(other)
        calls left_click() for tiles with coord
        in the 8 tiles around other'''
        for row in range(other.coord[0] - 1, other.coord[0] + 2): # tiles with row coordinates that are 1 less to one more than intitial
            for column in range(other.coord[1] - 1, other.coord[1] + 2): # tiles with column coordinates 1 less or 1 more
                if row >= 0 and column >= 0 and row <= self.height - 1 and column <= self.width - 1: # checkes to see if tiles are in grid
                    if not self.tiles[(row,column)].leftClicked: # auto clicks only if the tile has not been clicked before - stops from crashing
                        self.tiles[(row,column)].leftClicked = True
                        self.tiles[(row, column)].update_display()

    def find_number(self, other):
        '''Game.find_number(other) -> int
        finds tile number and return it'''
        number = 0 # counter
        if other.isbomb: # if tile is already bomb
            for row in range(other.coord[0]-1,other.coord[0]+2):
                for column in range(other.cord[1]-1,other.coord[1]+2):
                    if row>=0 and column>=0 and row <=self.height-1 and column<=self.width-1:
                        if self.tiles[(row,column)].isbomb:
                            number+=1
            number -= 1 # subtract 1 since tile is bomb
        else: # tile is not bomb
            for row in range(other.coord[0]-1,other.coord[0]+2):
                for column in range(other.coord[1]-1,other.coord[1]+2):
                    if row>=0 and column>=0 and row <=self.height-1 and column<=self.width-1:
                        if self.tiles[(row,column)].isbomb:
                            number+=1
        return number

    def update_display(self):
        '''Game.update_display
        changes number of tiles flagged at bottom'''
        self.counterLabel['text'] = str(self.numBombs-self.numFlag)

    def lost(self):
        '''Game.lost()
        prompts message
        changes color of the bomb tiles to red'''
        if not self.stopGame:
            for i in self.bombCoord: # makes bomb tiles red
                self.tiles[i]['bg'] = 'red'
                self.tiles[i]['text'] = '*'
            messagebox.showerror('Minesweeper', 'KABOOM! You lose.',parent=self) # shows message
            self.stopGame = True #doesn't run self.lost again

    def win(self):
        '''Game.win()
        prompts message'''
        if not self.stopGame:
            messagebox.showinfo('Minesweeper', 'Congratulations -- you won!', parent=self) # shows message
            self.stopGame = True


def play_minesweeper(width, height, numBombs):
    '''play_minesweeper(width, height, numBombs) -> runs game'''

    root = Tk()
    root.title('Minesweeper')
    grid = Game(root,width,height,numBombs)
    grid.mainloop()

    #

play_minesweeper(12,10,15)
