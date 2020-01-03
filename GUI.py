'''
CIS 41B Final Project, Fall 2019
Written by Stephen Wong and Jasmine Wong

This project has 3 files, the backend_oneCursorPerThread.py, the GUI.py, and the Statistics.py.
This is the GUI.py file. It is in charge of displaying all the information to the users through 5 Window classes.

NEW FEATURES USED:
#1. In the MainWindow class, clicking on the "MenuButton" will result in a pulldown menu for the user to 
select several states. Be sure to click on the 'OK' button after to see the results of the search.
#2. In the DialogWindow class's constructor, we implemented checkButtons for the user to click on. Unlike Radiobuttons,
checkButtons allow for multiple selection.

This file covers SQL querying, tkinter GUI module, and the OS module
'''
# These 5 lines necessary for displaying matplotlib. These 5 lines should be imported first above all other imports.
import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from Statistics import Statistics
import os
import sys
import sqlite3
import tkinter.filedialog
import tkinter.messagebox as tkmb
import copy

class MainWindow(tk.Tk):
    '''MainWindow is responsible for presenting the main GUI menu '''
    
    statesList = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]    
    
    designations = ["Park","Historic", "River", "Monument","Heritage", "Memorial", "Trail"]
    
    
    def __init__(self):
        super().__init__()
        
        self.title("NPS Database Application")   
        self.geometry("300x150")        
        
        linetxt = tk.Label(self,text = "Select National Park by criteria").grid(sticky='w')
        
        self._stateVar = tk.StringVar()
        self._stats = Statistics() # Create Statistics object for plotting data
       
        # New GUI feature #1: Implemented the tkinter Menubutton, which when clicked, will bring
        # down a pull down menu. In this case, we filled the pull down menu 
        # with radiobuttons for the user to choose from. 
        
        # When the user makes a 
        # choice and clicks the 'OK' button, then the DisplayWindow will show up with the
        # selected state's data.
        
        F1 = tk.Frame(self)
        F1.grid(row = 1)
        F2 = tk.Frame(self)
        F2.grid(row = 2)
        
        self._button1 = tk.Menubutton(F1, text='Select State', relief=tk.RAISED,
                                  activebackground='#3399ff',bg='white',fg='black')        
        self._button1.grid(row = 1,sticky = 'w')
        
        self._mb_radmenu = tk.Menu(self._button1)
        self._button1.configure(menu=self._mb_radmenu) # When clicked, button1 will bring up a menu       
        
        self._button2 = tk.Button(F1, text = "byDesignation", command = self.byDesignation).grid(row = 1, column = 1)  
        self._button3 = tk.Button(F1, text = "byCountry", command = self.byCountryStats).grid(row = 1, column = 2)
        self._button4 = tk.Button(F1, text = "byStats", command = self.byStateStats).grid(row = 1, column = 3)  
        self._button5 = tk.Button(F2, text = "by Latitude and Longitude", command = self.byLatitudeLongitudeStats).grid()
        
        self._okButton = tk.Button(F2, text = "OK", command = self.byState, bg = 'white').grid(row = 2, padx = 100)
        
        for state in MainWindow.statesList:
            self._mb_radmenu.add_radiobutton(label=state,variable=self._stateVar)
            
        # Open db connection 
        self._conn = sqlite3.connect('NPS.db') 
        self._cur = self._conn.cursor()
        
        self.protocol("WM_DELETE_WINDOW",self._onCloseWindow) # self._onCloseWindow will always run before window is closed
        
        
    # Bystate will simply create a pull down menu for the GUI, so I won't need
    # to call the DialogWindow. I will directly call DisplayWindow
    def byState(self):
        '''byState() allows the user to select one of 50 states, then select one NPS from that state,
        before displaying more detailed information'''
        statename = self._stateVar.get()
        
        # ListBoxWindow searches the state's national parks' names from SQL table        
        dialog = ListBoxWindow(self,statename)
        
        # Prevent the ListBoxWindow from immediately closing before 
        # retrieving the needed information below (getParkName())
        
        # This "self.wait_window(menu)" is a blocking function, so it prevents the 
        # next line of code from being run.
        self.wait_window(dialog)
        parkName = dialog.getParkName()
        
        if parkName != "":
            display = DisplayWindow(self,parkName,"name")
        
        
    def byDesignation(self):
        '''byDesignation() allows the user to view all US national parks
        based on one selected designation'''
                
        designationList = self.designations
        
        # create DialogWindow object, and pass the list into its constructor
        menu = DialogWindow(self,designationList,"designation")
        self.wait_window(menu) # MainWindow waits until DialogWindow is closed
        
        # After DialogWindow is closed, store selection in a tuple (tuple of designation names)
        designation = menu.getChoice()
        
        if designation != "":
            # create DisplayWindow object, and pass the tuple into its constructor   
            display = DisplayWindow(self,designation,"designations")
    
    
    def byCountryStats(self):
        '''byCountryStats opens the plot for NPS record of all 50 states'''     
        # create PlotWindow object, and pass the dict into its constructor
        
        dataPlot = PlotWindow(self)
        dataPlot.byCountryPlot()
     
        
    def byStateStats(self):
        '''byStateStats opens the plot for designations for 1-3 states,
        based on the user's choice'''
        
        # Then do menu = DialogWindow(self,designationList,"states"), and so 
        # returns a tuple of 1-3 states.
        
        # Call the SQL searching for those 3 states in the function. Since the 3 states number is 
        # small, this is still considered efficient. Do not preload all 50 states in Statistics.py
                
        menu = DialogWindow(self,MainWindow.statesList,"states")
        self.wait_window(menu) # MainWindow waits until DialogWindow is closed
        
        # After DialogWindow is closed, store selection in a tuple (tuple of state names)
        states = menu.getChoice()    

        
        if not states:
            return # End the function if the user did not choose any states

        # stateDesignationDict is a dict of lists.{CA: [5,10,0,...}, NY: [7,0,5,...]}
        stateDesignationDict = dict() 
        tempList = list()
    
        for state in states:
            tempList.clear()
            for designation in MainWindow.designations:

                sqlStatement = "SELECT COUNT(*) FROM NPStable WHERE states LIKE ? AND designation LIKE ?"
                currentState = "%" + state + "%"
                currentDesignation = "%" + designation + "%"
                params = (currentState, currentDesignation)

                self._cur.execute(sqlStatement, params)
                count = self._cur.fetchall()[0][0]
                tempList.append(count)
                
            stateDesignationDict[state] = copy.deepcopy(tempList)

        # Note: How will PlotWindow handle multiple data types?
        # I chose to pass it into one of the methods of the PlotWindow class instead.
        dataPlot = PlotWindow(self)
        dataPlot.byStatePlot(stateDesignationDict)    
     
        
    def byLatitudeLongitudeStats(self):
        '''byLatitudeLongitudeStats() opens up the latitude and longitude plot for 
        all NPS in the US'''
        dataPlot = PlotWindow(self)
        dataPlot.byLatitudeLongitudePlot()           
    
        
    def getCur(self):
        '''Return the current reference to the cursor object'''
        return self._cur    
    
    
    def getStats(self):
        '''Return the current reference to the Statistics object'''
        return self._stats
    
    
    def _onCloseWindow(self):
        '''_onCloseWindow forces the db connection to close before MainWindow
        is terminated'''
        self._conn.close()
        print("closed db")
        self.destroy()
    
        
# DialogWindow will accept a flag variable in its constructor to either use
# radio buttons or checkboxes.
class DialogWindow(tk.Toplevel):
    '''DialogWindow displays the list of choices for the user to choose from.
    For designations, enter the flag as "designations"
    For states, enter the flag as "states"                               '''
    
    
    def __init__(self, master, dataList, flag):
        super().__init__(master)
        
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self._onCloseWindow)
        self.grab_set()  # 'grab' event input, disable events for other windows
        self.focus_set() # set focus on current window
        self.transient(master) # remove extra icon on taskbar
        
        # In order to have a checkbox, then we need to have a list of 
        # StringVars, and we need a tuple of strings to pass back to MainWindow.
        
        self._choice = tk.StringVar()
        self._flag = flag
        
        # Use radiobutton for by designation
        if self._flag == "designation":

            self.title("Select one designation")
            self._choice.set(dataList[0]) # Set to first element by default
            for designation in dataList:       
                button = tk.Radiobutton(self, text=designation, variable=self._choice, value=designation).grid(sticky = 'w') 
                
        # Use checkboxes for user choosing states (change to 5 x 10)
        else: # If flag == "states"
            self.title("Select 1-3 states")
            self._choice = []
            self._vars = []
            
            row_num = 0
            col_num = 0

            for states in dataList:              
                var = tk.StringVar()
                
                # New GUI feature #2: Implemented the tkinter Checkbutton. When the user clicks on a Checkbutton,
                # it will fill it with the onvalue (the states's string here). When the user un-clicks on it, it will
                # fill it with an empty string. Checkbuttons allow for multiple selections.

                chk = tk.Checkbutton(self, text=states, variable=var, onvalue=states, offvalue="").grid(row = row_num, column = col_num)
                self._vars.append(var)
                
                col_num += 1
                if col_num == 10:
                    col_num = 0
                    row_num += 1
                    
        self._okButton = tk.Button(self, text = "OK", command = self._onclickedOK, bg = 'white').grid(row = 6, column = 5)   
          
              
    def getChoice(self):
        '''By designation: return a string 
           By states: return a tuple'''
        if self._flag == "designation":
            return self._choice.get()
        else: # If self._flag == "states"
            return tuple(self._choice) # Has already taken care of too many user choices
   
    
    def _onCloseWindow(self):
        '''
        [X] button clicked -> close dialog window, return to Main
        '''
        if self._flag == "designation":
            self._choice.set("") # Clear out choice variable to signify no choice
        else:
            self._vars = [] # Clear out variables so getChoice() returns []
        self.destroy()
       
        
    def _onclickedOK(self):
        '''Destroys the window if clicked OK.
        Only picks the first 3 states the user chooses.'''
        
        if self._flag == "states":
            self._choice = [var.get() for var in self._vars if var.get() != "" ] # Do not send back results that are unclicked by user.
            if len(self._choice) > 3:
                strMessage = "More than 3 states selected, only the first 3 states will be shown"
        
                if tkmb.showinfo("Number of choices", str(strMessage), parent = self): # Test if this works
                    self._choice = self._choice[0:3] # Get only the first 3 chosen            
        self.destroy()
   
        
# Since DialogWindow has too many responsibilities, ListBoxWindow acts as a secondary class.     
class ListBoxWindow(tk.Toplevel):
    '''ListBoxWindow class receives a US state, performs SQL searching, and displays all
    the national parks in that state in a ListBox. It then returns the user's choice of
    1 national park.'''
        
    def __init__(self, master, state):
        super().__init__(master)    
        
        self._master = master
        self._cur = self._master.getCur()
        
        self.grab_set()  
        self.focus_set() 
        self.transient(self._master)       
        
        self._choice = "" # Contains the name of the park that the user chooses
        
        self.title("Choose 1 National Park")
        self.geometry("500x250")
        self.protocol("WM_DELETE_WINDOW", self._onCloseWindow)
                
        S = tk.Scrollbar(self)
        self._LB = tk.Listbox(self,height=12, width=80,yscrollcommand=S.set)
        self._LB.grid(row=0,column=0)
        S.grid(row=0,column=1,sticky='ns') # Grid the scrollbar
        
        # Call back for listbox view function to change when scrollbar is moved
        S.config(command=self._LB.yview)
        
        # Perform SQL searching of database
        stateName = "%" + state + "%"
        sqlStatement = "SELECT name FROM NPStable WHERE states LIKE ?"
        params = (stateName, )
        
        self._cur.execute(sqlStatement, params)
        
        # Insert all national park names into the listbox
        self._parkNamesList = [nameTuple[0] for nameTuple in self._cur.fetchall()]
        self._LB.insert(tk.END, *self._parkNamesList)
        
        # When the user clicks on a park, call the callbackFunc
        self._LB.bind('<<ListboxSelect>>',self._callbackFunc)  
        
        # Create the OK button
        B = tk.Button(self,text="OK",command=self._onclickedOK)
        B.grid(row=13,padx = 215,sticky = 'w')
                
    def _callbackFunc(self,event):
        '''Updates the self._choice variable based on user selection''' 
        idx = self._LB.curselection()[0] # [0] is needed, since this is a tuple
        self._choice = self._parkNamesList[idx]
        
    def _onCloseWindow(self):
        '''
        [X] button clicked -> close dialog window, return to Main
        '''
        self._choice = "" # Clear out user choice so getParkName returns ""
        self.destroy()
        
    def _onclickedOK(self):
        '''Destroys the window if clicked OK.'''   
        self.destroy()
        
    def getParkName(self):
        '''Return a string containing 1 park name '''
        return self._choice
        
        
        
class DisplayWindow(tk.Toplevel):
    '''DisplayWindow displays the details of the user choices.
    flag - "state": search SQL database based on state
    flag - "name": search SQL database based on the name
    flag - "designations": search SQL database based on the designation + save to file option
    '''
    
    outFile = 'National Parks.txt'
    def __init__(self, master, detail,flag):
        super().__init__(master)
        
        self._master = master
        self._cur = self._master.getCur()
        
        self.grab_set()  
        self.focus_set() 
        self.transient(self._master)            
        
        self.geometry("730x420")
        
        F1 = tk.Frame(self, width=730, height=300)
        F1.grid(row = 0)        
                
        self._txt = tk.Text(F1, wrap=tk.WORD)
        self._txt.grid(row=0)
                         
        # The strings in the listbox are saved here and written to the actual file
        self._fileDataList = []
        
        # search SQL table based on the name of detail, and store the result 
        # as a class attribute
        
        #1. search SQL database for parks' names based on state
        #self.cur('SELECT parkname FROM NPStable WHERE ')
        if flag == "state":
            state = "%" + detail + "%"
            sqlStatement = "SELECT name FROM NPStable WHERE states LIKE ?"
            params = (state, )
            self._cur.execute(sqlStatement, params)
            
            for record in self._cur.fetchall():
                name = record[0]            
                self._txt.insert(tk.END, name)
                self._txt.insert(tk.END,"\n")
        
        
        #2. search SQL database for park's details based on the name of park
        
        # Used textbox instead of listbox in order to make description text wrap around
        elif flag == "name":
            # Create the Save button
            B = tk.Button(self,text="Save",command=self._saveData)
            B.grid(row=1,padx = 315,sticky = 'w')            
            
            name = detail
            sqlStatement = "SELECT name, designation,  description, directionsUrl FROM NPStable WHERE name = ?"
            params = (name, )  
            self._cur.execute(sqlStatement, params)
            

            for record in self._cur.fetchall():
                name = record[0]
                designation = record[1]
                description = record[2]
                directionsUrl = record[3]
                
                self._txt.insert(tk.END, name)
                self._txt.insert(tk.END,"\n")
                self._txt.insert(tk.END, designation)
                self._txt.insert(tk.END,"\n")
                self._txt.insert(tk.END, directionsUrl)  
                self._txt.insert(tk.END,"\n")
                self._txt.insert(tk.END,"\n")
                self._txt.insert(tk.END, description)
                
                self._fileDataList.append(name)
                self._fileDataList.append(designation)
                self._fileDataList.append(directionsUrl)
                self._fileDataList.append(description)
            
        #3. search by designation
        # Since there are too many types of designation, create a set of 
        # simpler designations. (Examine the types of designations she sent in 
        # email and simplify them)
                    
        # Then search SQL database using the %like% based on the user choice.
        else:
            designation = "%" + detail + "%"
            sqlStatement = "SELECT name FROM NPStable WHERE designation LIKE ?"
            params = (designation, )
            
            self._cur.execute(sqlStatement, params)
            
            for record in self._cur.fetchall():
                name = record[0]            
                self._txt.insert(tk.END, name)
                self._txt.insert(tk.END,"\n")                
        
    
    def _saveData(self):
        '''The saveData function prompts the user for a directory before
        creating and appending data to a file'''       
        
        # tkinter works with window manager to make the professional window.
        # Either '.' or os.getcwd() gets the current directory
        
        # So the default directory is the current directory, otherwise
        # the user could choose some other directory
        chosenpath = tk.filedialog.askdirectory(initialdir = '.')
        
        # Do not save if the user clicked 'X' on the save File window
        if chosenpath == "":
            return 
        
        filename = os.path.join(chosenpath, DisplayWindow.outFile)
       
        # Write all data in the DataWindow into the file
        with open(filename,'a') as fh: # Here, 'a' stands for append to file.
            for line in self._fileDataList:
                fh.write(line.replace('. ', '.\n') + "\n")
            fh.write("\n\n")
        
        strMessage = "Your search result is saved in " + DisplayWindow.outFile + " in " + chosenpath
        if tkmb.showinfo("Number of choices", str(strMessage), parent = self):
            self.destroy() # Close the DataWindow           
        
class PlotWindow(tk.Toplevel):
    '''PlotWindow is responsible for displaying the matplotlib and 
    seaborn plots to the user.
    
     Design:
     Create a "rent" object in the MainWindow class,
     and call the object's plotting functions in PlotWindow before
     having the GUI as a wrapper for the plot. '''
    
    def __init__(self, master):
        super().__init__(master)  
        self._master = master
        self._stats = self._master.getStats()
        
    def byCountryPlot(self):
        '''The function byCountryPlot calls and displays the plot for the total number 
        of nps for all states.'''        
                        
        fig = plt.figure(figsize = (9,6))
        self._stats.plotCountryStats()
        
        canvas = FigureCanvasTkAgg(fig, master = self)
        canvas.get_tk_widget().grid()
        canvas.draw()  # This will take care of the plt.show()        
        
    def byStatePlot(self,statesDict):
        '''The function byStatePlot calls and displays the histogram plot for 
        destinations of 1-3 cities'''
        #print("byStatePlot")
        
        # For the seaborn catplot, I cannot do 'fig = plt.figure(figsize = (11,8))'.,
        # as catplot actually returns the figure.
        
        # So, in the Statistics.py, I need to set plot = seaborn.catplot(...),
        # and then return plot.fig in order to display this.
        
        # Since we are displaying plot.fig instead of matplotlib, all plotting features
        # must be adjusted through plot.fig, not plt!
        
        
        #fig = plt.figure(figsize = (11,8))
        figure = self._stats.plotStatesStats(statesDict)
        
        # Instead of passing matplotlib to the Canvas, we pass the figure directly from catplot into
        # the Canvas.
        # canvas = FigureCanvasTkAgg(fig, master = self)
        canvas = FigureCanvasTkAgg(figure, master = self)
        
        canvas.get_tk_widget().grid()
        canvas.draw()  # This will take care of the plt.show()  
        
    def byLatitudeLongitudePlot(self):
        '''The function byLatitudeLongitudePlot displays the latitude and longitude
        of each NPS in the US, and provides a linear regression line for where the most
        common parks are centered.'''        
                        
        fig = plt.figure(figsize = (9,6))
        self._stats.plotLatitudeLongitudeStats()
        
        canvas = FigureCanvasTkAgg(fig, master = self)
        canvas.get_tk_widget().grid()
        canvas.draw()  # This will take care of the plt.show()        
        
def gui2fg():
    """Brings tkinter GUI to foreground on Mac
       Call gui2fg() after creating main window and before mainloop() start
    """
    if sys.platform == 'darwin':  
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))
        
    
        
def main():
    win1 = MainWindow()
    gui2fg()
    win1.mainloop()  
    
if __name__ == "__main__":
    main()
