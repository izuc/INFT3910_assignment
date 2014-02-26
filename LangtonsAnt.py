#Langton's Ant - INFT3910 Assignment 3
#Created 28/04/2010
#Author: Lance Baker

#Import packages
from Tkinter import *
import tkFileDialog
import pylab as py
import sqlite3 as sql
from PIL import Image, ImageTk, ImageGrab
import os.path
import time

#Class that holds the variables for the ant direction (Compass)
class Compass:
    North = 1
    South = 2
    East = 3
    West = 4

class Ant:
    def __init__(self, grid):
        self.grid = grid
        self.setup()
        
    def setup(self):
        self.posx = self.grid.sx / 2
        self.posy = self.grid.sy / 2                   
        self.dir = Compass.East
        self.ruleString = [[0, 'white'], [1,'black'], [1,'green']]
        self.steps = 0

        
    def checkBoundary(self, position):
        if (position > 99):
            position = 0
        elif(position < 0):
             position = 99
        return position
        
    def flipState(self):
        try:
            self.posy = self.checkBoundary(self.posy)
            self.posx = self.checkBoundary(self.posx)
            index = (self.grid.gridpoints[self.posy][self.posx][2] + 1) % (len(self.ruleString))
            rule = self.ruleString[index]
            self.grid.gridpoints[self.posy][self.posx][2] = index
            self.grid.gridpoints[self.posy][self.posx][0] = rule[0]
            self.grid.itemconfigure(self.grid.gridpoints[self.posy][self.posx][1], fill=rule[1])
        except:
            print("")

    def setDirAndMove(self):
        def move(position, rule):
            if (rule):
                position += 1
            else:
                position -= 1
            return position

        rule = self.grid.gridpoints[self.posy][self.posx][0]
        if self.dir == Compass.North:
            self.dir = (Compass.West, Compass.East)[rule]
            self.posx = move(self.posx, rule)
        elif self.dir == Compass.East:
            self.dir = (Compass.North, Compass.South)[rule]
            self.posy = move(self.posy, rule)
        elif self.dir == Compass.South:
            self.dir = (Compass.East, Compass.West)[rule]
            self.posx = move(self.posx, not rule)
        elif self.dir == Compass.West:
            self.dir = (Compass.South, Compass.North)[rule]
            self.posy = move(self.posy, not rule)
        self.flipState()
        self.steps += 1

#Class that has our control variables       
class Control:
    Start=1
    Running=2
    Stop=3

    
class Grid(Canvas):
    def __init__(self, application, sizeX, sizeY):
        Canvas.__init__(self, application, bg='white', width=600, height=600)
        self.sx = sizeX
        self.sy = sizeY
        self.state = Control.Start
        self.ant = Ant(self)
        self.application = application
        self.pack(fill=BOTH)
        #self.db.getCurrentRun()
        
    def initGridPoints(self):
        self.gridpoints = []
        for i in range(self.sy):
            self.row = []
            for j in range(self.sx):
                self.row.append([0, None, 0, None]) #index, reference, state, id
            self.gridpoints.append(self.row)
            
    def drawGrid(self):
        pointerx = 0
        pointery = 0
        count = 1
        self.initGridPoints()
        for i in range(self.sy):
                for j in range(self.sx):
                    self.gridpoints[i][j][1] = self.create_rectangle(pointerx, pointery, pointerx+4, pointery+4, fill="white")
                    self.gridpoints[i][j][3] = count
                    pointerx += 6
                    count += 1
                pointery += 6
                pointerx = 0

    def stop(self):
        if (self.state == Control.Running):
            self.state = Control.Start
            self.ant.setup()
            self.application.db.commit()
            print "DATABASE COMIT"

    def start(self):
        try:
            if (self.state == Control.Start):
                self.drawGrid()
                self.state = Control.Running
                self.application.db.newRun()
            #stepLimit = 0
            while (self.state == Control.Running): 
                self.ant.setDirAndMove()
                self.update()
                self.application.db.saveStep(self.gridpoints[self.ant.posy][self.ant.posx][3], self.ant.steps)

                try:
                    Application.strAntPos.set(self.gridpoints[self.ant.posy][self.ant.posx][3])
                    Application.strTimeSteps.set(self.ant.steps)
                except Exception, e:
                    print e  
        except:
            print("Application Ended")
            print(sys.exc_info()[0])
        print "ended loop"

class Graph:
    strLineFormat = ""
    def __init__(self):
        Graph.strLineFormat = "-"

    def setTitles(self, strTitle, strXName, strYName):
        #Sets graph labels
        py.xlabel(strXName)
        py.ylabel(strYName)
        py.title(strTitle)

    #plots the runs onto the graph
    def plotLines(self, lstPlots, lstSelected):
        intCounter = 1
        #loops through list and adds runs to the plot
        for plot in lstPlots:
            py.plot(len(plot),10,plot, "-",label='run ' + str(intCounter))
            intCounter +=1
            
        #strLegend = str(lstSelected)
        py.legend(lstSelected)
    #Sets the line           
    def setLineFormat(self, strLine):
        if(strLine != ""):
            Graph.strLineFormat = strLine
            
    def returnLineFormat(self):
        return Graph.strLineFormat
            
    def showGraph(self):
        py.show()

class DataGrid(Frame):
    def __init__(self, master, lists, rowSelectAction):
        Frame.__init__(self, master)
        self.lists = []
        self.rowSelectAction = rowSelectAction
        for l,w in lists:
            frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0, relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self); frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set
        
    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'
    
    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'
    
    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'
    def _scroll(self, *args):
        for l in self.lists:
            apply(l.yview, args)
            
    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last: return apply(map, [None] + result)
        return result
    
    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        self.rowSelectAction(first)
        for l in self.lists:
            l.selection_set(first, last)
                 
class Database:
    def __init__(self):
        #The constructor, needs to check if the database file doen't exsist,
        #And if so it needs to run the sql.
        if os.path.isfile('ant.db'):
            self.conn = sql.connect('ant.db')
            self.cur = self.conn.cursor()
        else:
            self.conn = sql.connect('ant.db')
            self.cur = self.conn.cursor()
            self.createDB()

        self.currentRun = None

    def createDB(self):
        #Need to run this if the DB doesn't exsist.
        self.cur.execute('CREATE TABLE IF NOT EXISTS runs(runId INTEGER PRIMARY KEY AUTOINCREMENT, run_date DATETIME)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS ant(id INTEGER PRIMARY KEY AUTOINCREMENT, runId INTEGER, step INTEGER, pos INTEGER)')

        self.conn.commit()
        
    def saveStep(self, pos, step):
        #Save an ant's current step.
        self.cur.execute('INSERT INTO ant(runId, step, pos) VALUES('+str(self.currentRun)+', '+str(step)+', '+str(pos)+')')
        #self.conn.commit()

    def insert(self, strings):
        #No longer used, but might be useful latr for inserting
        #stuff into the DB.
        for q in strings:
            self.cur.execute(q)
            self.conn.commit()

    def commit(self):
        #Commits the data into the database
        self.conn.commit()

    def newRun(self):
        #Sets the calue for the next run
        #newRun =  + 1
        self.cur.execute('INSERT INTO runs(run_date) VALUES(DATETIME(\'NOW\'))')
        self.cur.execute('SELECT runId FROM runs ORDER BY runId DESC LIMIT 1')
        for data in self.cur: 
            self.currentRun = data[0]

        print "current run: ", self.currentRun

    def returnRun(self, runNumber):
        lstRun = []
        self.cur.execute('SELECT * FROM ant WHERE runId = ' + str(runNumber))
        for row in self.cur:
            lstRun.append(row[3])

        return lstRun

    def getRuns(self):
        data = []
        self.cur.execute('SELECT * FROM runs ORDER BY run_date ASC')
        for row in self.cur:
            data.append(row)
        return data
        
class Application(Frame):
    strAntPos = ""
    strTimeSteps = ""
    
    def __init__(self, master):
        Frame.__init__(self, master, width=650, height=650)
        self.grid = Grid(self, 100, 100)
        self.db = Database()
        self.createToolbar(master)
        self.createRightToolbar(master)
        self.createTopToolbar(master)
        self.pack()

    def showRules(self):
        window = Toplevel()
        window.title('Rule Settings')
        
        Label(window, text="Colour: ", width=5, anchor=W).grid(row=0, column=0, sticky=NW)
        txtColour = Entry(window, name="colour", width=25)
        listbox = Listbox(window, width=25, height=6)
        for item in ["white", "black", "blue", "red", "pink", "green"]:
            listbox.insert(END, item)

        listbox.grid(row=0, column=1, sticky=E)

        ruleInt = IntVar()        
        Label(window, text="Rule: ", width=5, anchor=W).grid(row=1, column=0, sticky=W)
        R1 = Radiobutton(window, text="Left", variable=ruleInt, value=0)
        R1.grid(row=1, column=1, sticky=W)
        R2 = Radiobutton(window, text="Right", variable=ruleInt, value=1)
        R2.grid(row=1, column=1, sticky=E)
        
        self.rowSelected = 0

        def rowSelectAction(row):
            self.rowSelected = row
            
        grid = DataGrid(window, (('ID', 20), ('Colour', 10), ('Rule', 10)), rowSelectAction)
        grid.grid(row=2, column=0, columnspan=2)
        
        
        def addRule():
            try:
                colour = listbox.get(listbox.curselection()[0]) 
                grid.insert(END, (len(self.grid.ant.ruleString), colour, ruleInt.get()))
                self.stateGrid.insert(END, (colour, ruleInt.get()))
                self.grid.ant.ruleString.append([ruleInt.get(), colour])
            except:
                print("You must select a value first")
            
        def removeRule():
            grid.delete(self.rowSelected)
            self.stateGrid.delete(self.rowSelected)
            del self.grid.ant.ruleString[self.rowSelected]
            
        
        for index, cell in enumerate(self.grid.ant.ruleString):
            grid.insert(END, (index, cell[1], cell[0]))

        try:
            btnSave = Button(window, text="Save", width=10, command=addRule)
            btnSave.grid(row=3, column=0, sticky=W)
        except:
            print "Must enter a rule and corresponding colour before adding."

        btnRemove = Button(window, text="Remove", width=10, command=removeRule)
        btnRemove.grid(row=3, column=1, sticky=E)
        
    def showGraph(self):
        lstSelectedGraphs = []
        window = Toplevel()
        window.title('History')
        run_data = self.db.getRuns()
        
        self.rowSelected = 0
        
        def displaySelectedGraph():
            #Checks to see if our list is empty, if so, use the selected row (meaning only one selected)
            if(len(lstSelectedGraphs) == 0):
                lstSelectedGraphs.append(self.rowSelected+1)
                
            #Checks to see if we have any data
            if (len(run_data) > 0):
                gr = Graph()
                gr.setTitles('History Comparison', 'Time Steps', 'Ant Position')
                
                lstPlots = []

                #loops through all the runs and compiles another list of run results
                for item in lstSelectedGraphs:    
                    lstPlots.append(self.db.returnRun(item))

                #Sorts list
                lstSelectedGraphs.sort()
                #Displays graph
                print "Displaying Graphs for runs: " + str(lstSelectedGraphs)
                gr.plotLines(lstPlots, lstSelectedGraphs)
                gr.showGraph()

        #Sets the selected row
        def rowSelectAction(row):
            self.rowSelected = row

        def addRun():
            #Boolean used to flag graphs already selected
            blnFound = False
            #Checks to see if this is the first value or not
            if(len(lstSelectedGraphs) > 0):
                #loops through items in our list
                for item in lstSelectedGraphs:
                    #Checks to see if it has found the selected value in the list
                    if(int(item) == int(run_data[self.rowSelected][0])):
                        blnFound = True
                #if its not found, then add the run to the list
                if(not blnFound):        
                    lstSelectedGraphs.append(run_data[self.rowSelected][0])
                    strSelected.set(str(lstSelectedGraphs))
            else:
                lstSelectedGraphs.append(run_data[self.rowSelected][0])
                strSelected.set(str(lstSelectedGraphs))

        def removeRun():
            del lstSelectedGraphs[-1:]
            strSelected.set(str(lstSelectedGraphs))
            
        #Creates labels and our data grid            
        labelHeading = Label(window, anchor="w",text="Here you can select one or more runs to display a graph on.\nTo select one graph, simply highlight the run and click 'Display'.\nTo select multiple graphs, select a run and hit 'Add', continue\nuntil all graphs have been selected, then click 'Display'")
        labelHeading.grid(row=0, columnspan=2, sticky=W+N+E+S)    
        lblSpace = Label(window, anchor="ne", width=10)
        lblSpace.grid(row=1, columnspan=2, sticky=W+N)
        grid = DataGrid(window, (('Run #', 10), ('Date Time', 50)), rowSelectAction)
        grid.grid(row=2, column=0, columnspan=3)

        #Inserts the run data into the data grid
        for result in run_data:
            grid.insert(END, (result[0], result[1]))

        #initialises our text variable for selected graphs
        strSelected = StringVar()
        strSelected.set("")

        #Creates all the buttons and labels
        
        lblSelectGraph = Label(window, text="Selected Graphs:",anchor="w")
        lblSelectGraph.grid(row=3, column=1, rowspan=2, sticky=W)
        lblSelected = Label(window, textvariable=strSelected,anchor="w")
        lblSelected.grid(row=3, column=2, rowspan=2, sticky=W)
        btnSelect = Button(window, text="Add", width=10, command=addRun)
        btnSelect.grid(row=3, column=0, padx=10,pady=10, sticky=W)
        btnRemove = Button(window, text="Remove", width=10, command=removeRun)
        btnRemove.grid(row=4, column=0, padx=10,pady=5, sticky=W)
        btnDisplay = Button(window, text="Display", width=10, command=displaySelectedGraph)
        btnDisplay.grid(row=5, column=0,padx=10,pady= 10, sticky=W)
        btnClose = Button(window, text="Close", width=10, command=window.destroy)
        btnClose.grid(row=5, column=1, columnspan=2, padx=10,pady=10, sticky=W)
            
    def showAbout(self):
        about = Toplevel()
        about.title('About')
        #Creates string variable for our content label
        strContent = StringVar()
        strContent.set('Content')
        labelHeading = Label(about, text="About", width=30).grid(row=0, sticky=W+N+E+S)
        labelContent = Label(about, textvariable=strContent).grid(row=1, sticky=W+N, padx=10)
        strContent.set("This application was developed for INFT3910 Assignment 3.")
        lblMembers = Label(about, text="By Lance Baker 2010").grid(pady=10, row=2, column=0, columnspan=3,sticky=W+N+E)

        #Creates buttons and the logo image
        logoImage = Image.open("Ant.jpg")
        size = 100, 100
        logoImage.thumbnail(size)
        logoTK = ImageTk.PhotoImage(logoImage)
        canvasLogo = Canvas(about, width=95, height=90, bg="white", bd=0)
        canvasLogo.create_image(50, 48, image=logoTK)
        canvasLogo.grid(row=1, column=2, columnspan=2, rowspan=2, sticky=W+N, padx=20, pady=5)
        canvasLogo.image = logoTK
        btnClose = Button(about, text="Close", width=10, command=about.destroy)
        btnClose.grid(row=3, column=3, pady=10, sticky=W)
        
    def createToolbar(self, master):
        #Creates bottom toolbar with our control buttons
        self.toolbar = Frame(master)
        Button(self.toolbar, text="Start", width=10, command=self.grid.start).pack(side=LEFT, padx=2, pady=2)
        Button(self.toolbar, text="Stop", width=10, command=self.grid.stop).pack(side=LEFT, padx=2, pady=2)
        Button(self.toolbar, text="Graph", width=10, command=self.showGraph).pack(side=LEFT, padx=2, pady=2)
        Button(self.toolbar, text="Exit", width=10, command=master.destroy).pack(side=RIGHT, padx=2, pady=2)
        self.toolbar.pack(side=BOTTOM, fill=X)

    def createRightToolbar(self, master):
        master.toolbar = Frame(master)
        master.update()
        
        #Creates label frame for our controls
        group = LabelFrame(master, text="Details", padx=5, pady=5)
        group.grid(row=1, columnspan=2)
        group.pack(padx=10, pady=10, side=RIGHT,anchor="nw")

        #Initialises the text variables for the labels
        Application.strAntPos = StringVar()
        Application.strAntPos.set("")
        Application.strTimeSteps = StringVar()
        Application.strTimeSteps.set("")

        #Creates relevant labels
        lblTime = Label(group, text="Time steps:", anchor="ne", width=10).grid(row=0, column=0, sticky=W+N)
        lblPostion = Label(group, text="Postition:", anchor="ne", width=10).grid(row=1, column=0, sticky=W+N)

        lblDisplayTime = Label(group, anchor="nw", textvariable=Application.strTimeSteps, width=25).grid(row=0, column=1, sticky=W+N)
        lblDisplayPosition = Label(group, anchor="nw", textvariable=Application.strAntPos, width=25).grid(row=1, column=1, sticky=W+N)
        lblSpace = Label(group, anchor="ne", width=10).grid(row=3, column=0, sticky=W+N)
        lblRule = Label(group, text="Rules:", anchor="w", width=10).grid(row=4, column=0, sticky=W+N)

        #Sets the row selected
        def rowSelectAction(row):
            self.rowSelected = row
            
        #Instantiates the data grid and its location on the grid    
        self.stateGrid = DataGrid(group, (('Colour', 10), ('Rule', 10)), rowSelectAction)
        self.stateGrid.grid(row=5, column=0, columnspan=2, sticky=W+E)

        #inserts values into the data grid
        for index, cell in enumerate(self.grid.ant.ruleString):
            self.stateGrid.insert(END, (cell[1], cell[0]))
            
        master.toolbar.pack(side=RIGHT, fill=Y)

    #Function that captures a screenshot   
    def captureScreenShot(self, master):
        #Gets the save file info from the user
        filename = tkFileDialog.asksaveasfilename(defaultextension="jpg")
        #Updates master window
        master.update()

        #Gets location from the geometry string
        strGeoInfo = str(master.winfo_geometry())
        intIndexPlus1 = str.find(strGeoInfo, '+', 0, len(strGeoInfo))
        strSub1 = strGeoInfo[intIndexPlus1 + 1:]
        
        intIndexPlus2 = str.find(strSub1, '+', 0, len(strSub1))

        strSub2 = strSub1[intIndexPlus2+1:]
        strSub1 = strSub1[:-(intIndexPlus2+1)]
        
        if(filename != ""):
            #Catch statement for any errors in the location found above
            try:
                #Updates the master form again
                master.update()
                #Grabs a screenshot and saves it to the directory and name from the save dialog above
                ImageGrab.grab().save(filename)
                print "Saved screenshot to: " + filename
            except:
                print "Screen size not in integer format."            
        else:
            print "Screenshot has been cancelled."
        
    def createTopToolbar(self, master):
        menubar = Menu(master)

        #Add file menu option
        filemenu = Menu(menubar)  
        filemenu.add_command(label="Quit", command=root.destroy) #Better than root.quit
        menubar.add_cascade(label="File", menu=filemenu)

        #Add controls option
        controlsmenu = Menu(menubar)
        controlsmenu.add_command(label="Start", command=self.grid.start) 
        controlsmenu.add_command(label="Stop", command=self.grid.stop)
        controlsmenu.add_separator()
        controlsmenu.add_command(label="Save Image", command=lambda i=master: self.captureScreenShot(i))
        menubar.add_cascade(label="Controls", menu=controlsmenu)

        #Add tools option
        toolsmenu = Menu(menubar)
        toolsmenu.add_command(label="Graph", command=self.showGraph)
        toolsmenu.add_separator()       
        toolsmenu.add_command(label="Rules", command=self.showRules)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

        #Add about menu option    
        aboutmenu = Menu(menubar)
        aboutmenu.add_command(label="About", command=self.showAbout)
        menubar.add_cascade(label="Help", menu=aboutmenu)

        master.config(menu=menubar)
        
if __name__ == "__main__":
    root = Tk()
    root.title('Langton\'s Ant')
    #Make window fixed size
    root.resizable(width=FALSE, height=FALSE)
    #Updates root window
    root.update()
    toolbar = Frame(root)
    Application(root).mainloop()
