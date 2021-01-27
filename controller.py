from time import sleep






##### stuff I added for gui #####

### WINDOW SCALE FACTOR ###
### CHANGE THIS IF YOU HAVE A REALLY HIGH RESOLUTION DISPLAY THAT MAKES THE UI WINDOW TINY ###
wsf = 1.0


import keyboard
from tkinter import *

mode = "play"
lock = "off"
hold = "off"
noteButton = {}
keyLabel = {}

tuneSelect = "a"

#################################







'''
import serial
'''

pitches = [174,183,197,209,218,229,241,268,279,296,316,325]

# serial setup
'''
ser = serial.Serial(
	port = '/dev/cu.usbmodem14101',
	baudrate = 2400,
)
'''

# set the pitch of a particular note
# address must be a string of length 1
def set_pitch(address, pitch):
    '''
    address = ord(address)
    data = [address, ord('0')]
    ser.write(bytes(data))
    #print(bytes(data))
    hundreds = int(pitch/100)
    pitch = pitch - 100 * hundreds
    tens = int(pitch/10)
    ones = int(pitch - 10 * tens)
    for i in range(hundreds):
        data = [address, ord('6')]
        ser.write(bytes(data))
        #print(bytes(data))
    for i in range(tens):
        data = [address, ord('5')]
        ser.write(bytes(data))
        #print(bytes(data))
    for i in range(ones):
        data = [address, ord('4')]
        ser.write(bytes(data))
        #print(bytes(data))
    '''
    print("Set %s to %s" % (address, pitch))

def turn_on(address):
    '''
    data = [ord(address), ord('9')]
    ser.write(bytes(data))
    '''
    print("%s on" % address)

def turn_off(address):
    '''
    data = [ord(address), ord(':')]
    ser.write(bytes(data))
    '''
    print("%s off" % address)









#######################
### TKINTER GARBAGE ###
#######################

# Class used to represent a single note
class noteKey:
    
    def __init__(self, name, label, keylabel):
        self.name = name
        self.label = label
        self.keylabel = keylabel
        self.state = 'off'
        self.keyboardState = 'off'
        self.pitch = -99
        self.savedPitch = -99

    def mouseDown(self, event=None):
        if mode == 'play':
            if lock == 'off':
                if self.state == 'off':
                    self.on()
            if lock == 'on':
                if self.state in ('on','lock'):
                    self.off()
                elif self.state == 'off':
                    self.on()
        if mode == 'tune':
            self.select()

    def mouseUp(self, event=None):
        if mode == 'play':
            if lock == 'off':
                if self.state == 'on' and self.keyboardState == 'off':
                    self.off()
            if lock == 'on':
                if self.state == 'on':
                    self.lock()
    
    # The 'keyboard state' variable tells you whether the note was last activated by a keypress
    # or a mouse click; this prevents weirdness from happening when mouseclicks and keypresses
    # are being used together
    
    def keyDown(self):
        if mode == 'play':
            if lock == 'off':
                if self.state == 'off' and self.keyboardState == 'off':
                    self.on()
                    self.keyboardState = 'on'
            if lock == 'on':
                if self.state in ('on','lock'):
                    self.off()
                elif self.state == 'off':
                    self.on()
                    self.keyboardState = 'on'
        if mode == 'tune':
            self.select()
        
    def keyUp(self):
        if mode == 'play':
            if lock == 'off':
                if self.state == 'on' and self.keyboardState == 'on':
                    self.off()
            if lock == 'on':
                if self.state == 'on' and self.keyboardState == 'on':
                    self.lock()

    def on(self):
        turn_on(self.name)
        self.state = 'on'
        noteButton[self.name].config(highlightthickness=5, highlightbackground='green')

    def off(self):
        turn_off(self.name)
        self.state = 'off'
        self.keyboardState = 'off'
        noteButton[self.name].config(highlightthickness=0, highlightbackground='white')

    def lock(self):
        self.state = 'lock'
        noteButton[self.name].config(highlightthickness=5, highlightbackground='lightgreen')
    
    def hold(self):
        self.state = 'hold'
        noteButton[self.name].config(highlightthickness=5, highlightbackground='lightgreen')
    
    # Function used for storing temporary values in the 'tuning' menu
    def select(self):
        pitchLabel.config(text = "%s:" % self.label)
        
        global tuneSelect
        notes[tuneSelect].pitch = pitchField.get()
        tuneSelect = self.name
        
        for i in notes:
            noteButton[i].config(highlightthickness=0, highlightbackground='white')
            noteButton[self.name].config(highlightthickness=5, highlightbackground='red')
            
        pitchField.delete(0, END)
        pitchField.insert(10, self.pitch)
    
    # Writes frequency to chip if it meets various criteria
    def write(self):
        try:
            if int(self.pitch) > 0:
                if int(self.pitch) == self.savedPitch:
                    raise Exception("%s no pitch change to write" % self.name)
                self.savedPitch = int(self.pitch)
            else:
                raise Exception("%s out of range" % self.name)
            set_pitch(self.name, self.pitch)
        except Exception as e:
            print(e)
            self.pitch = self.savedPitch

# Function for toggling pitch lock, which determines whether notes release on key up or on a second keypress
def toggleLock(event=None):
    global mode
    global lock
    global notes
    
    if mode == "play":
        if lock == "on":
            lock = "off"
            print ("key lock off")
            lockButton.config(highlightthickness = 0, highlightbackground='white', text = "\nOFF\n        z")

            for i in notes:
                if notes[i].state == 'lock':
                    notes[i].off()
            
        elif lock == "off":
            lock = "on"
            print ("key lock on")
            lockButton.config(highlightthickness = 5, highlightbackground='green', text = "\nON\n        z")

# Function for toggling 'sustain'. When enabled, any pitches currently being played will be held indefinitely
# until sustain is disabled. It may be of limited usefulness.
def toggleHold(event=None):
    global mode
    global hold
    global notes
    
    if mode == "play":
        
        if hold == "off":
            hold = "on"
            print ("sustain on")
            holdButton.config(highlightthickness = 5, highlightbackground='green', text = "\nON\n        c")
                
            for i in notes:
                if notes[i].state in ('on', 'lock'):
                    notes[i].hold()
                    
        elif hold == "on":
            hold = "off"
            print ("sustain off")
            holdButton.config(highlightthickness = 0, highlightbackground='white', text = "\nOFF\n        c")
            
            for i in notes:
                if notes[i].state == 'hold':
                    notes[i].off()

# Changes UI to tuning menu
def tune(event=None):
    global mode
    for i in notes:
        notes[i].off()
    mode = "tune"
    
    eraseMain()
    drawTune()
    
    pitchField.delete(0, END)
    pitchField.insert(10, notes[tuneSelect].pitch)
    
    notes[tuneSelect].select()
    
    pitchField.focus()

# Writes any changes made to tuning
def writePitches():
    global mode
    
    notes[tuneSelect].pitch = pitchField.get()
    
    for i in notes:
        notes[i].write()
        noteButton[i].config(highlightthickness=0, highlightbackground='white')
    
    eraseTune()
    drawMain()

    mode = "play"

# Exit tuning menu without writing changes
def discardPitches():
    global mode
    
    for i in notes:
        notes[i].pitch = notes[i].savedPitch
        noteButton[i].config(highlightthickness=0, highlightbackground='white')
        
    eraseTune()
    drawMain()
    
    mode = "play"

# A dictionary of all 12 note objects. Confusingly, each has four alphabetic values associated with it.
# First, the dictionary key; Second, the chip address, which is equivalent to the dictionary key;
# Third, the musical note value, which is displayed on the buttons themselves; and Fourth, the keyboard
# value which will trigger the note.
notes = {
    'a':noteKey('a','F','a'),
    'b':noteKey('b','F#','w'),
    'c':noteKey('c','G','s'),
    'd':noteKey('d','G#','e'),
    'e':noteKey('e','A','d'),
    'f':noteKey('f','A#','r'),
    'g':noteKey('g','B','f'),
    'h':noteKey('h','C','g'),
    'i':noteKey('i','C#','y'),
    'j':noteKey('j','D','h'),
    'k':noteKey('k','D#','u'),
    'l':noteKey('l','E','j')
    }

# GUI initialization, and adding event triggers for the lock and sustain toggle buttons
mainWindow = Tk()
mainWindow.resizable(False,False)
mainWindow.geometry('%dx%d' % (630*wsf,270*wsf))
mainWindow.title("Instrument Controller")

mainWindow.bind('z',toggleLock)
mainWindow.bind('c',toggleHold)

# Creates the onscreen musical keyboard
for i in notes:
    noteButton[i] = Button(mainWindow, text = "\n%s\n         %s" % (notes[i].label,notes[i].keylabel), font = ("Arial",int(14*wsf),"normal"))
    noteButton[i].bind('<Button-1>', notes[i].mouseDown)
    noteButton[i].bind('<ButtonRelease-1>', notes[i].mouseUp)
    noteButton[i].config(highlightthickness=0, highlightbackground='white')

    

####################
### DRAWING CODE ###
####################

# Main UI elements
titleLabel = Label(mainWindow, text="Fantomakontrol", fg = "grey", font = ("Verdana",int(40*wsf),"bold"))

lockLabel = Label(mainWindow, text="Key lock:", font = ("Arial",int(14*wsf),"normal"))
lockButton = Button(mainWindow, text=("\nOFF\n         z"), font = ("Arial",int(14*wsf),"normal"), command = toggleLock)
lockButton.config(highlightthickness=0, highlightbackground='white')

holdLabel = Label(mainWindow, text="Sustain:", font = ("Arial",int(14*wsf),"normal"))
holdButton = Button(mainWindow, text=("\nOFF\n         c"), font = ("Arial",int(14*wsf),"normal"), command = toggleHold)
holdButton.config(highlightthickness=0, highlightbackground='white')

tuneButton = Button(mainWindow, text=("Set Pitches"), font = ("Arial",int(16*wsf),"normal"), command = tune)
tuneButton.config(highlightthickness=0, highlightbackground='white')


# Tuning UI elements
pitchLabel = Label(mainWindow, text = "", font = ("Arial",int(30*wsf),"normal"))
pitchField = Entry(mainWindow, font = ("Arial",int(30*wsf),"normal"))
hzLabel = Label(mainWindow, text = "Hz", font = ("Arial",int(30*wsf),"normal"))

writeButton = Button(mainWindow, text=("Write"), fg = "green", font = ("Arial",int(16*wsf),"bold"), command = writePitches)
cancelButton = Button(mainWindow, text=("Cancel"), fg = "red", font = ("Arial",int(16*wsf),"normal"), command = discardPitches)

# Draws the main menu
def drawMain():
    global wsf
    
    lockLabel.place(x=32*wsf,y=185*wsf)
    lockButton.place(x=40*wsf,y=210*wsf,width=50*wsf,height=50*wsf)
    holdLabel.place(x=155*wsf,y=185*wsf)
    holdButton.place(x=160*wsf,y=210*wsf,width=50*wsf,height=50*wsf)
    tuneButton.place(x=520*wsf,y=60*wsf,width=100*wsf,height=30*wsf)

# Erases the main menu
def eraseMain():
    lockLabel.place_forget()
    lockButton.place_forget()
    holdLabel.place_forget()
    holdButton.place_forget()
    tuneButton.place_forget()

# Draws the tuning menu
def drawTune():
    global wsf
    
    pitchLabel.place(x=155*wsf, y=198*wsf, anchor = 'ne')
    pitchField.place(x=155*wsf, y=200*wsf, width=100*wsf, height=40*wsf)
    hzLabel.place(x=255*wsf, y=198*wsf)
    writeButton.place(x=320*wsf,y=205*wsf,width=90*wsf,height=30*wsf)
    cancelButton.place(x=420*wsf,y=205*wsf,width=90*wsf,height=30*wsf)

# Erases the tuning menu
def eraseTune():
    pitchLabel.place_forget()
    pitchField.place_forget()
    hzLabel.place_forget()
    writeButton.place_forget()
    cancelButton.place_forget()

# Draws the keyboard and giant title, which persist through menu changes
def drawKeyboard():
    global wsf
    
    ### TITLE ###
    titleLabel.place(x = 315*wsf, y = 0*wsf, anchor = "n")

    ### WHITES ###
    noteButton['a'].place(x=10*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['c'].place(x=70*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['e'].place(x=130*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['g'].place(x=190*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['h'].place(x=250*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['j'].place(x=310*wsf,y=120*wsf,width=50*wsf,height=50*wsf)
    noteButton['l'].place(x=370*wsf,y=120*wsf,width=50*wsf,height=50*wsf)

    ### BLACKS ###
    noteButton['b'].place(x=40*wsf,y=60*wsf,width=50*wsf,height=50*wsf)
    noteButton['d'].place(x=100*wsf,y=60*wsf,width=50*wsf,height=50*wsf)
    noteButton['f'].place(x=160*wsf,y=60*wsf,width=50*wsf,height=50*wsf)
    noteButton['i'].place(x=280*wsf,y=60*wsf,width=50*wsf,height=50*wsf)
    noteButton['k'].place(x=340*wsf,y=60*wsf,width=50*wsf,height=50*wsf)


drawKeyboard()
drawMain()




########################
### KEYPRESS GARBAGE ###
########################

# Note: These strings correspond to note addresses, NOT the character values of their associated keyboard keys
macOS_key_codes = {
    0:'a',
    13:'b',
    1:'c',
    14:'d',
    2:'e',
    15:'f',
    3:'g',
    5:'h',
    16:'i',
    4:'j',
    32:'k',
    38:'l'
}

# Function that gets triggered whenever something happens on the keyboard. Gets a list of keys currently pressed,
# and checks them against a list of keys we actually care about, and sends commands to the note objects
def keyList(event):
    keysDown = [x for x in keyboard._pressed_events]
    
    for x in macOS_key_codes:
        if x in keysDown:
            notes[macOS_key_codes[x]].keyDown()
        else:
            notes[macOS_key_codes[x]].keyUp()

keyboard.hook(keyList)

# Tkinter loop which makes the program not exit
mainWindow.mainloop()