from tkinter import*
import random as rd
import time
import numpy
import sys
from random import randrange

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
#    - 2 end moves (1 A and 2 B)
NMOVES = 2 + 2 + 2

#---------------------------------------------
# SEED AND RANDOM GENERATOR
#---------------------------------------------

seed = 52
rd.seed(seed)

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
timeDelayRefresh = 2

#---------------------------------------------
# TRACK MOVE VARIABLES
#---------------------------------------------

hpsMvsA = []
hpsMvsB = []
rxnMvsA = []
rxnMvsB = []

hpsPtrA = []
hpsPtrB = []
rxnPtrA = []
rxnPtrB = []

nHA = 0
nHB = 0
nRA = 0
nRB = 0

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

#*********************************************
# METHODS AND FUNCTIONS
#*********************************************

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
# DO MOVE FUNCTIONS
#---------------------------------------------

# Makes an end move
def do_end_mv(site, actTi):
    
    # Get the exchange site
    site1 = site
    sqAux1 = sqArray[site1]
    pT1 = sqAux1.get_pType()
    
    # Set the canvas text
    set_canvas_text(pT1, actTi)
        
    # Change the colors for the borders
    change_bd(site1, altCol)
    set_canvas_arrow(actTi, site1, MAK)
    time.sleep(timeDelayRefresh)
    
    # Set the new particle
    newPart = EMPTY
    
    # Check that it's a valid swap
    if((actTi == DESORB and pT1 == EMPTY) or (actTi == ADSORB and pT1 != EMPTY)):
        
        print("Illegal end move:")
        
        if(actTi == DESORB):

            print("Desorb particle failed, particle at end site: " + pT1)
        
        elif(actTi == ADSORB):
        
            print("Adsorb particle failed, particle at end site: " + pT1)
            
        sys.exit("Error message")
    
    # Adsorb or desorb a particle
    if(actTi == ADSORB):
        
        rN = rand_real3() * (adsRateA + adsRateB)
        newPart = AA
        
        if(rN < adsRateB):
            
            newPart = BB
        
    # Set the particle
    sqAux1.set_pType(newPart)
    
    # Change the colors for the borders
    time.sleep(timeDelayRefresh) 
    change_bd(site1, stdCol)
    set_canvas_arrow(actTi, site1, DEL)
    
    # Update the sites around the site
    update_lst_after_em(site1)

# Makes a particle swap
def do_hop_mv(site, partType):
    
    # Set the canvas text
    set_canvas_text(partType, HOPPMV)
    
    # Get the exchange site
    site1 = site
    site2 = site + 1
    
    # Get the sites to exchange
    sqAux1 = sqArray[site1]
    sqAux2 = sqArray[site2]
    
    # Get the particles in the sites
    pT1 = sqAux1.get_pType()
    pT2 = sqAux2.get_pType()
        
    # Change the colors for the borders
    change_bd(site1, altCol)
    change_bd(site2, altCol)
    set_canvas_arrow(HOPPMV, site1, MAK)
    time.sleep(timeDelayRefresh)
    
    # Check that it's a valid swap
    if(not((pT1 == partType and pT2 == EMPTY) or (pT1 == EMPTY and pT2 == partType))):
        print("Illegal exchange of particles:")
        print("Site 1 = " + str(site1) + ", Particle to move in site 1: " + str(pT1))
        print("Site 2 = " + str(site2) + ", Particle to move in site 2: " + str(pT2))
        print("Particle to exchange = " + str(partType))
        sys.exit("Error message")
    
    # Change the particles
    sqAux1.set_pType(pT2)
    sqAux2.set_pType(pT1)
    
    # Change the colors for the borders
    time.sleep(timeDelayRefresh)      
    change_bd(site1, stdCol)
    change_bd(site2, stdCol)
    set_canvas_arrow(HOPPMV, site1, DEL)
    
    # Update the sites around the site
    update_lst_after_swp(site1)

# Makes a particle reaction
def do_rxn_mv(site, partType):
    
    # Set the canvas text
    set_canvas_text(partType, RXNPMV)
    
    # Get the exchange site
    site1 = site
    
    # Get the sites to exchange
    sqAux1 = sqArray[site1]
    
    # Get the particles in the sites
    pT1 = sqAux1.get_pType()
        
    # Change the colors for the borders
    change_bd(site1, altCol)
    set_canvas_arrow(RXNPMV, site1, MAK)
    time.sleep(timeDelayRefresh)
    
    # Check that it's a valid swap
    if(pT1 != partType):
        
        print("Illegal reaction move:")
        print("Site = " + site1 + "Particle chosen to react: " + pT1)
        print("Original particle to react = " + partType)
        sys.exit("Error message")
    
    # Change the particles
    sqAux1.set_pType((pT1 + 1) % 2)
    
    # Change the colors for the borders
    time.sleep(timeDelayRefresh)      
    change_bd(site1, stdCol)
    set_canvas_arrow(RXNPMV, site1, DEL)
    
    # Update the sites around the site
    update_lst_after_rxn(site1)

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
# RATE RELATED FUNCTIONS
#---------------------------------------------

# Calculates the rates of the system
def rate_calc():
    
    global rates
       
    # Set the rates for hopping moves
    i = 0
    rates[i] = hA * float(nHA)
    i = i +1
    rates[i] = rates[i-1] + hB * float(nHB)
    
    # Set the rates for the end moves
    
    # For site = 0
    i = i +1
    site = 0
    if(sqArray[site].get_pType() == EMPTY):

        rates[i] = rates[i-1] + (adsRateA + adsRateB)
        
    elif(sqArray[site].get_pType() == AA):
    
        rates[i] = rates[i-1] + desorpRateA

    elif(sqArray[site].get_pType() == BB):
    
        rates[i] = rates[i-1] + desorpRateB
    
    # For site = (PORELEN - 1)
    i = i + 1
    site = (PORELEN - 1)
    if(sqArray[site].get_pType() == EMPTY):
         
        rates[i] = rates[i-1] + (adsRateA + adsRateB)
            
    elif(sqArray[site].get_pType() == AA):
               
        rates[i] = rates[i-1] + desorpRateA
                  
    elif(sqArray[site].get_pType() == BB):
                     
        rates[i] = rates[i-1] + desorpRateB
        
    # Set the rates for the reaction moves
    i = i +1
    rates[i] = rates[i-1] + rxnA * float(nRA)
    i = i +1
    rates[i] = rates[i-1] + rxnB * float(nRB)

# Chooses a move from the list of possible moves
def rate_select():
    
    global hpsMvsA, hpsMvsB, nHA, nHB, nRA, nRB, rates, rxnMvsA, rxnMvsB
    
    # Choose a random number according to the total rate
    rN = rand_real3() * rates[NMOVES - 1]
    
    if(rN < rates[0]):
        
        site = randrange(0, nHA)
        site = hpsMvsA[site]
        do_hop_mv(site, AA)
        
    elif(rN < rates[1]):
        
        site = randrange(0, nHB)
        site = hpsMvsB[site]
        do_hop_mv(site, BB)
        
    elif(rN < rates[2]):
        
        stat = DESORB
        if(sqArray[0].get_pType() == EMPTY):
            stat = ADSORB
        do_end_mv(0, stat)
        
    elif(rN < rates[3]):
        
        stat = DESORB
        if(sqArray[PORELEN - 1].get_pType() == EMPTY):
            stat = ADSORB
        do_end_mv(PORELEN - 1, stat)
        
    elif(rN < rates[4]):
        
        site = randrange(0, nRA)
        site1 = rxnMvsA[site]
        do_rxn_mv(site1, AA)
        
    elif(rN < rates[5]):
        
        site = randrange(0, nRB)
        site1 = rxnMvsB[site]
        do_rxn_mv(site1, BB)
        
    else:
        
        print("Incorrectly chosen rate.")
          
#---------------------------------------------
# SET FUNCTIONS
#---------------------------------------------

# Sets the canvas text
def set_canvas_arrow(actIon, site1, makOdel):
    
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
            
            num3 = sqAux.get_y0_coord() + int(boxLen/2)
            
            if(sqAux.get_pType() != EMPTY):
                
                num1 = sqAux.get_x0_coord() + int(boxLen/2)
                num2 = sqAux.get_x1_coord() + int(boxLen/2)
                
            elif(sqAux.get_pType() == EMPTY):
                
                num1 = sqAux.get_x1_coord() + int(boxLen/2)
                num2 = sqAux.get_x1_coord() - int(boxLen/2)
            
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
            
            st1 = "adsorption"
        
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
# SETUP FUNCTIONS
#---------------------------------------------

# Setups the simulation
def setup_sim():
    
    global nHA, nHB, nRA, nRB
    
    nHA = 0
    nHB = 0
    nRA = 0
    nRB = 0
    
    for i in range(0, PORELEN):
            
        hpsMvsA.append(-1)
        hpsMvsB.append(-1)
           
        hpsPtrA.append(-1)
        hpsPtrB.append(-1)
           
        rxnMvsA.append(-1)
        rxnMvsB.append(-1)

        rxnPtrA.append(-1)
        rxnPtrB.append(-1)

    for i in range(0, NMOVES):
        
        rates.append(0.0)
    
    # Update the sites at the beginning
    for i in range(0, PORELEN):
        
        update_lst_swp(i)
        update_lst_rxn(i)

#---------------------------------------------
# UPDATE AFTER MOVE FUNCTIONS
#---------------------------------------------

# Update lists after a swap move
def update_lst_after_em(site):
    
   # Choose the site to update
   update_lst_swp(site - 1)
   update_lst_swp(site)
   update_lst_swp(site + 1)
   
   update_lst_rxn(site)

# Update lists after a swap move
def update_lst_after_rxn(site):
    
    # Update the swap lists
    update_lst_swp(site - 1)
    update_lst_swp(site)
    
    # Update the reaction lists
    update_lst_rxn(site)
    
# Update lists after a swap move
def update_lst_after_swp(site):
    
    # Update the swap lists
    update_lst_swp(site - 1)
    update_lst_swp(site)
    update_lst_swp(site + 1)
    
    # Update the reaction lists
    update_lst_rxn(site)
    update_lst_rxn(site + 1)
    
#---------------------------------------------
# UPDATE LISTS FUNCTIONS
#---------------------------------------------

# Update the lists for swap moves
def update_lst_rxn(site):
    
    global nRA, nRB
    
    if(not(site >= 0 and site <= (PORELEN - 1))):
        return None
    
    if(nRA > 0 and rxnA > 0.0):
        
        nRA = update_lst_delete_site(site, rxnPtrA, rxnMvsA, nRA)
        
    if(nRB > 0 and rxnB > 0.0):
        
        nRB = update_lst_delete_site(site, rxnPtrB, rxnMvsB, nRB)
        
    # Get the particles at the sites
    pT1 = sqArray[site].get_pType()
    
    if(pT1 == AA and rxnA > 0.0):
        
        nRA = update_lst_add_site(site, rxnPtrA, rxnMvsA, nRA)
        
    elif(pT1 == BB and rxnB > 0.0):
        
        nRB = update_lst_add_site(site, rxnPtrB, rxnMvsB, nRB)

# Update the lists for swap moves
def update_lst_swp(site):
    
    global nHA, nHB
    
    if(not(site >= 0 and site < (PORELEN - 1))):
        return None
    
    if(nHA > 0 and hA > 0.0):
        
        nHA = update_lst_delete_site(site, hpsPtrA, hpsMvsA, nHA)
        
    if(nHB > 0 and hB > 0.0):
        
        nHB = update_lst_delete_site(site, hpsPtrB, hpsMvsB, nHB)
        
    # Get the particles at the sites
    pT1 = sqArray[site].get_pType()
    pT2 = sqArray[site+1].get_pType()
    
    if(((pT1 == EMPTY and pT2 == AA) or (pT1 == AA and pT2 == EMPTY)) and hA > 0.0):
        
        nHA = update_lst_add_site(site, hpsPtrA, hpsMvsA, nHA)
        
    elif(((pT1 == EMPTY and pT2 == BB) or (pT1 == BB and pT2 == EMPTY)) and hB > 0.0):
        
        nHB = update_lst_add_site(site, hpsPtrB, hpsMvsB, nHB)


#---------------------------------------------
# UPDATE LISTS GENERAL FUNCTIONS
#---------------------------------------------

# Add move to the array of moves
def update_lst_add_site(site, ptrLst, mvsLst, nMvs):
    
    # Modify the pointer list and the move list
    ptrLst[site] = nMvs
    mvsLst[nMvs] = site
    
    # Return the number of moves incremented by one
    return int(nMvs + 1)
    
# Delete a move from the array of moves
def update_lst_delete_site(site, ptrLst, mvsLst, nMvs):
    
    # Get the move id
    move_id = ptrLst[site]
    
    # If the site doesn't exist don't bother
    if(not(nMvs > 0 and move_id >= 0)):
        return int(nMvs)
    
    # Delete the move from the move list
    mvsLst[move_id] = mvsLst[nMvs - 1]
    mvsLst[nMvs  - 1] = -1
    
    # Delete the move from pointer list
    ptrLst[mvsLst[move_id]] = move_id
    ptrLst[site] = -1
    
    # Decrease the number of moves by 1
    return int(nMvs - 1)
   
#---------------------------------------------
# MAIN FUNCTION
#---------------------------------------------

def main_func():
    
    # Get the elements
    get_squares()
    setup_sim()
    timeEll = 0.0
    
    # Create the squares that will contain the labels/ information
    set_canvas_boxes()
    
    # Run the code while true
    while True:
        rate_calc()
        timeEll = timeEll - numpy.log(rand_real3())/rates[NMOVES - 1]
        canvas.itemconfig(txtTimeEll, text = "Time Elapsed = " + str(timeEll))
        tk.update()
        rate_select()    

#---------------------------------------------
# RUN THE PROGRAM
#--------------------------------------------- 
main_func()
tk.mainloop()
