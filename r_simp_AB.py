from tkinter import*
import random as rd
import time
from scipy.stats.vonmises_cython import numpy

#---------------------------------------------
# PORE CONSTANTS
#---------------------------------------------

# The width and height of the cells
boxLen = 30

# The particle types
AA = 0
BB = 1
EMPTY = 2

# The length of the pore
PORELEN = 30

# Move identifiers
RXN = 1
HOP = 2

# Adsorption/desorption identifiers
ADSORB = 1
DESORB = 2
RXNPMV = 3
HOPPMV = 4

# Delete or Make identifier
DEL = 1
MAK = 2

# The number of possible moves of the system:
#    - 2 hop moves A and B
#    - 2 reaction moves A and B
#    - 4 end moves (2 A and 2 B)
NMOVES = 2 + 2 + 4

#---------------------------------------------
# PORE RATES AND VARIABLES
#---------------------------------------------

# Hop and reaction rates
hA = 1.0
hB = 1.0
rxnA = 0.1
rxnB = 0.0

# Outside concentrations
xEquilA = 0.8
xEquilB = 0.0
xEquilT = xEquilA + xEquilB

# Adsorption/Desorption rates
desorpRateA = hA * (1.0 - xEquilT) 
desorpRateB = hB * (1.0 - xEquilT)
adsRateA = hA * xEquilA 
adsRateB = hB * xEquilB

#---------------------------------------------
# TIME VARIABLES
#---------------------------------------------

# The elapsed time
timeEll = 0.0

# The rates of the system
rates = [ ]

# The time delay for refreshing (in seconds)
timeDelayRefresh = 1

#---------------------------------------------
# PICTURE CONTAINERS AND PROPERTIES
#---------------------------------------------

# The array that will hold the squares
sqArray = []

# The length and width of the canvas
wd = (4 + PORELEN) * boxLen
he = 200

# Border and fill colors
altCol = "magenta"
stdCol = "black"

AClr = "#00FFFF"
BClr = "orange"
EMPTYClr = "white"

cvTxt = ""
txtTimeEll = ""
linArr = ""

#---------------------------------------------
# CONFIG THE CANVAS
#---------------------------------------------

# Create the tkinter module and pack the canvas
tk = Tk()
canvas = Canvas(tk, width = wd, height = he)
tk.title("Drawing")
canvas.pack()

#---------------------------------------------
# CLASSES AND SPECIAL FUNCTIONS
#---------------------------------------------

# Class for the squares
class PartCell:
    
    # Initialize the variables  
    def __init__(self,val):
        
        self.x0Coord = val
        self.x1Coord = self.x0Coord + boxLen
        self.y0Coord = 80
        self.y1Coord = self.y0Coord + boxLen
        
        # Choose which particle to place
        self.pType = EMPTY
        self.color = EMPTYClr
        if(rand_real3() < xEquilT):
            rN = rand_real3() * xEquilT
            self.pType = AA
            self.color = AClr
            if(rN < xEquilB):
                self.pType = BB
                self.color = BClr
        
        self.rect = canvas.create_rectangle(self.x0Coord,self.y0Coord,self.x1Coord,self.y1Coord, fill = self.color) 
        self.change_fill_color()
    
    # Set the color of the border
    def change_border_color(self, nCol):
        
        # Change the color to the new one
        canvas.itemconfig(self.rect, outline = nCol)
        tk.update()
    
    # Set the color of the box
    def change_fill_color(self):
        
        # Choose the color according to the particle type
        if(self.pType == EMPTY):
            self.color = EMPTYClr
        elif(self.pType == AA):
            self.color = AClr
        else:
            self.color = BClr
        
        # Change the color to the new one
        canvas.itemconfig(self.rect, fill = self.color)
        tk.update()
    
    # Gets the particle type in the cell
    def get_pType(self):
        
        return self.pType
    
    # Gets the particle type in the cell
    def get_x0_coord(self):
        
        return self.x0Coord
    
    # Gets the particle type in the cell
    def get_x1_coord(self):
        
        return self.x1Coord
    
    # Gets the particle type in the cell
    def get_y0_coord(self):
        
        return self.y0Coord
    
    # Gets the particle type in the cell
    def get_y1_coord(self):
        
        return self.y1Coord
    
    # Change the particle type and the color of the cell
    def set_pType(self, newType):
        
        self.pType = newType
        self.change_fill_color()

#---------------------------------------------
# RANDOM FUNCTIONS
#---------------------------------------------

def rand_real3():
    
    # Define a random number
    rN = rd.random()
    
    # Fix the random number
    while(rN == 0.0):
        rN = rd.random()
    
    # Return the random number
    return rN

#---------------------------------------------
# METHODS AND FUNCTIONS
#---------------------------------------------

# Calculates the rates of the system
def calc_rates():
    
    # Initialize the rates array
    i = 0
    while(i < NMOVES):
        rates.append(0.0)
        i = i + 1
    
    # Set the rates
    i = 0
    rates[i] = 2.0 * hA * float(PORELEN)
    i = i +1
    rates[i] = rates[i-1] + 2.0 * hB * float(PORELEN)
    
    i = i +1
    rates[i] = rates[i-1] + 2.0 * desorpRateA
    i = i +1
    rates[i] = rates[i-1] + 2.0 * desorpRateB
    
    i = i +1
    rates[i] = rates[i-1] + 2.0 * adsRateA
    i = i +1
    rates[i] = rates[i-1] + 2.0 * adsRateB
    
    i = i +1
    rates[i] = rates[i-1] + rxnA * float(PORELEN)
    i = i +1
    rates[i] = rates[i-1] + rxnB * float(PORELEN)
        
# Chooses a move from the list of possible moves
def select_rate():
    
    # Choose a random number according to the total rate
    rN = rand_real3() * rates[NMOVES - 1]
    
    if(rN < rates[0]):
        
        do_hop_mv(AA)
        
    elif(rN < rates[1]):
        
        do_hop_mv(BB)
        
    elif(rN < rates[2]):
        
        do_end_mv(AA,DESORB)
        
    elif(rN < rates[3]):
        
        do_end_mv(BB,DESORB)
        
    elif(rN < rates[4]):
        
        do_end_mv(AA,ADSORB)
        
    elif(rN < rates[5]):
        
        do_end_mv(BB,ADSORB)
        
    elif(rN < rates[6]):
        
        do_rxn_mv(AA)
        
    elif(rN < rates[7]):
        
        do_rxn_mv(BB)
        
    else:
        
        print("Incorrectly chosen rate.")

#---------------------------------------------
# HOP FUNCTIONS
#---------------------------------------------

# Makes an end move
def do_end_mv(partType, actTi):
    
    # Set the label for the canvas
    set_canvas_text(partType, actTi)
    
    # Choose the site to adsorb/desorb the particle
    site = 0
    if(rand_real3() < 0.5):
        site = PORELEN - 1
    
    # Get the information
    sqAux = sqArray[site]
    
    set_canvas_arrow(actTi, site, site, MAK)
    change_bd(site, altCol)
    time.sleep(timeDelayRefresh)
    
    # Depending on the type of move, do the move
    if(actTi == ADSORB and sqAux.get_pType() == EMPTY):
    
        sqAux.set_pType(partType) 
        
    elif(actTi == DESORB and sqAux.get_pType() == partType):
    
        sqAux.set_pType(EMPTY)
    
    else:
    
        change_canvas_text("Wrong particle chosen - Forbidden move.")
    
    time.sleep(timeDelayRefresh)
    change_bd(site, stdCol)
    set_canvas_arrow(actTi, site, site, DEL)

# Makes a particle swap
def do_hop_mv(partType):
    
    set_canvas_text(partType, HOPPMV)
    
    # Initialize the variables
    site = rd.randrange(0, PORELEN)
    sqAux = sqArray[site]
        
    # Choose the side towards which the particle should move
    site1 = site + 1
    if(rand_real3() < 0.5):
        site1 = site - 1
    
    # Show the colors for the borders
    change_bd(site, altCol)
    change_bd(site1, altCol)
    set_canvas_arrow(HOPPMV, site, site1, MAK)
    time.sleep(timeDelayRefresh)
    
    # Check that it's a valid swap
    if(partType == sqAux.get_pType()):
        
        #Check the validity of the site chosen
        if(site1 >= 0 and site1 < PORELEN):
            
            sqAux1 = sqArray[site1]
            if(sqAux1.get_pType() == EMPTY):      
            
                sqAux.set_pType(EMPTY)
                sqAux1.set_pType(partType)
            
            else:
            
                if(partType == AA):
                    
                    change_canvas_text("Move Type = Hop to the side an A particle - Forbidden move.")
                else:
                        
                    change_canvas_text("Move Type = Hop to the side a B particle - Forbidden move.")
        else:
            
            change_canvas_text("Not an end move - Forbidden move.")
                
    else:
        
        change_canvas_text("Wrong particle chosen - Forbidden move.")
           
    time.sleep(timeDelayRefresh)      
    change_bd(site, stdCol)
    change_bd(site1, stdCol)
    set_canvas_arrow(HOPPMV, site, site1, DEL)
    
#---------------------------------------------
# REACTION FUNCTIONS
#---------------------------------------------

# Makes a particle reaction
def do_rxn_mv(partType):
    
    set_canvas_text(partType, RXNPMV)
    
    # Choose a reaction site
    site = rd.randrange(0, PORELEN)
    
    set_canvas_arrow(RXNPMV, site, site, MAK)
    
    # Change the color of the border to show it
    change_bd(site, altCol)
    time.sleep(timeDelayRefresh)
    
    # Check that the particle is able to react
    if(sqArray[site].get_pType() == partType):
    
        # Change the particle type
        sqArray[site].set_pType((partType+1) % 2)
    else:
        change_canvas_text("Wrong particle chosen - Unable to react.")
        time.sleep(timeDelayRefresh)
    
    # Return the border to the original color
    change_bd(site, stdCol)
    set_canvas_arrow(RXNPMV, site, site, DEL)

#---------------------------------------------
# CHANGE FUNCTIONS
#---------------------------------------------

# Changes the border of the selected site
def change_bd(site, nCl):
    
    if(site >= 0 and site < PORELEN):
        
        sqArray[site].change_border_color(nCl)

# Makes a particle reaction
def change_canvas_text(tSt):
    
    global cvTxt
    
    num = int(sqArray[int(PORELEN/2)].get_x1_coord()-boxLen/2)
    
    if cvTxt == "" :
        cvTxt = canvas.create_text((num,10), text = tSt)
    else:
        canvas.delete(cvTxt)
        cvTxt = canvas.create_text((num,10), text = tSt)
    
    tk.update()

#---------------------------------------------
# GET FUNCTIONS
#---------------------------------------------

# Sets the square array
def get_squares():
    
    for i in range(0,PORELEN):
        
        if(i == 0):
            sqArray.append(PartCell(i * boxLen + 1.5 * boxLen))
        else:
            sqArray.append(PartCell(sqArray[i-1].get_x1_coord() + 1))
          
          
#---------------------------------------------
# SET FUNCTIONS
#---------------------------------------------

# Sets the canvas text
def set_canvas_arrow(actIon, site1, site2, makOdel):
    
    global linArr
    
    # Initialize the variables
    num1 = 0
    num2 = 0
    num3 = 0
    num4 = 0
    num5 = 0
    num6 = 0
    num7 = 0
    num8 = 0
    
    sqAux = sqArray[site1]
    
    if(makOdel == MAK):
        
        if(actIon == ADSORB):
            
            if(site1 == 0):
            
                num1 = sqAux.get_x0_coord() - int(boxLen/2)
                num2 = sqAux.get_x0_coord() + int(boxLen/2)
            
            elif(site1 == PORELEN - 1):
            
                num1 = sqAux.get_x1_coord() + int(boxLen/2)
                num2 = sqAux.get_x1_coord() - int(boxLen/2)
            
            num3 = sqArray[site1].get_y0_coord() + int(boxLen/2)
            linArr = canvas.create_line(num1, num3, num2, num3, arrow = LAST)
        
        elif(actIon == DESORB):
            
            if(site1 == 0):
            
                num1 = sqAux.get_x0_coord() + int(boxLen/2)
                num2 = sqAux.get_x0_coord() - int(boxLen/2)
            
            elif(site1 == PORELEN - 1):
            
                num1 = sqAux.get_x1_coord() - int(boxLen/2)
                num2 = sqAux.get_x1_coord() + int(boxLen/2)
            
            num3 = sqAux.get_y0_coord() + int(boxLen/2)
            linArr = canvas.create_line(num1, num3, num2, num3, arrow = LAST)
        
        elif(actIon == RXNPMV):
            
            num1 = sqAux.get_x1_coord() - int(boxLen/2) - 5
            num3 = sqAux.get_x1_coord() - boxLen
            num5 = sqAux.get_x1_coord()
            num7 = sqAux.get_x1_coord() - int(boxLen/2) + 5
    
            num2 = sqAux.get_y0_coord() + int(boxLen/2)
            num4 = sqAux.get_y0_coord() - boxLen
            num6 = sqAux.get_y0_coord() - boxLen
            num8 = sqAux.get_y0_coord() + int(boxLen/2)
    
            linArr = canvas.create_line(num1, num2, num3, num4, num5, num6, num7, num8, arrow = LAST)
    
        elif(actIon == HOPPMV):
            
            num1 = sqAux.get_x0_coord() + int(boxLen/2)
            num3 = sqAux.get_y0_coord() + int(boxLen/2)
            
            if(site1 < site2):
                
                num2 = sqAux.get_x0_coord() + int(boxLen/2) + boxLen
                
            elif(site1 > site2):
                
                num2 = sqAux.get_x0_coord() + int(boxLen/2) - boxLen
            
            linArr = canvas.create_line(num1, num3, num2, num3, arrow = LAST)
    
    elif(makOdel == DEL):
   
        canvas.delete(linArr)
    
    tk.update()
        
        
# Sets the canvas text
def set_canvas_boxes():
    
    global txtTimeEll
    
    sqAux = sqArray[int(PORELEN/2)]
    
    x0Coord1 = sqAux.get_x0_coord() - 6 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + boxLen
    canvas.create_rectangle(x0Coord1, y0Coord1, x0Coord1 + boxLen, y0Coord1 + boxLen, fill = AClr)
    
    x0Coord1 = sqAux.get_x0_coord() - 5 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + int(3* boxLen/2)
    canvas.create_text(x0Coord1, y0Coord1 + boxLen, text = "A")
    
    x0Coord1 = sqAux.get_x0_coord() - 2 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + boxLen
    canvas.create_rectangle(x0Coord1, y0Coord1, x0Coord1 + boxLen, y0Coord1 + boxLen, fill = BClr)
    
    x0Coord1 = sqAux.get_x0_coord() - 1 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + int(3* boxLen/2)
    canvas.create_text(x0Coord1, y0Coord1 + boxLen, text = "B")
    
    x0Coord1 = sqAux.get_x0_coord() + 2 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + boxLen
    canvas.create_rectangle(x0Coord1, y0Coord1, x0Coord1 + boxLen, y0Coord1 + boxLen, fill = EMPTYClr)
    
    x0Coord1 = sqAux.get_x0_coord() + 3 * int(boxLen/2)
    y0Coord1 = sqAux.get_y1_coord() + int(3* boxLen/2)
    canvas.create_text(x0Coord1, y0Coord1 + boxLen, text = "EMPTY")
    
    x0Coord1 = sqAux.get_x0_coord() + int(boxLen/2)
    y0Coord1 = sqAux.get_y0_coord() - int(3* boxLen/2)
    txtTimeEll = canvas.create_text(x0Coord1, y0Coord1 + boxLen, text = "Time Elapsed = 0.0")

    change_canvas_text("")

# Sets the canvas text
def set_canvas_text(partType, actTi):
    
    if(actTi == ADSORB or actTi == DESORB):
  
        # Get the proper strings
        st1 = "desorption"
        if(actTi == ADSORB):
            
            st1 = "ddsorption"
        
        st2 = " an A"
        if(partType == BB):
            
            st2 = "a B"
    
        change_canvas_text("Move Type = Do end move, " + st1 + " of " + st2 + " particle.")
        
    elif (actTi == RXNPMV):
        
        # Change the name of the canvas
        if(partType == AA):
            
            change_canvas_text("Move Type = Change A -> B.")
            
        else:    
            
            change_canvas_text("Move Type = Change B -> A.")
            
    elif (actTi == HOPPMV):
        
        # Change the name of the canvas
        if(partType == AA):
            
            change_canvas_text("Move Type = Hop to the side an A particle.")
        
        else:
                
            change_canvas_text("Move Type = Hop to the side a B particle.")


          
#---------------------------------------------
# MAIN FUNCTION
#---------------------------------------------

def main_func():
    
    # Get the elements
    get_squares()
    calc_rates()
    timeEll = 0.0
    
    # Create the squares that will contain the labels/ information
    set_canvas_boxes()
    
    # Run the code while true
    while True:
        timeEll = timeEll - numpy.log(rand_real3())/rates[NMOVES - 1]
        canvas.itemconfig(txtTimeEll, text = "Time Elapsed = " + str(timeEll))
        tk.update()
        select_rate()    

#---------------------------------------------
# RUN THE PROGRAM
#--------------------------------------------- 
main_func()
tk.mainloop()