'''
CIS 41B Final Project, Fall 2019
Written by Jasmine Wong and Stephen Wong 

This project has 3 files, the backend_oneCursorPerThread.py, the GUI.py, and the Statistics.py.

This is the Statistics.py file. It covers the plotCountryStats, plotStatesStats, plotLatitudeLongitudeStats functions,
which each generate one plot (either through the native plotting functions in matplotlib, or seaborn's plotting functions).

This file covers matplotlib, numpy, pandas, seaborn, database modules.

NEW FEATURES USED: pandas' database access, pandas' data manipulation, seaborn's statistical plotting (regression plot & categorial plot)
'''

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine

class Statistics:
    ''' class variables '''
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"] 
    designations = ["Park","Historic", "River", "Monument","Heritage", "Memorial", "Trail"]
    colors = ["red", "green", "blue"]
    
    def __init__(self):
        # Call these searches on the SQL table seperately from the GUI file
        # We will have two seperate data structures for this class
        
        # 1st data struct - self._countryDict: {state1: number of nps, state2: number of nps, ...}
        # During final plot, call lambda: sort by value on the dict
        
        # For the designations for each state, don't preload data for all 50 states
        # into the constructor of this class. Rather, MainWindow will perform the searching,
        # pass the data to this class, and then plotStatesStats() will process it.
        self._countryDict = dict()
        self._conn = sqlite3.connect('NPS.db') 
        self._cur = self._conn.cursor()        
        for state in Statistics.states:
            currentState = "%" + state + "%"
            
            sqlStatement = "SELECT name FROM NPStable WHERE states LIKE ?"
            params = (currentState, )
           
            self._cur.execute(sqlStatement, params)
            count = 0
            for record in self._cur.fetchall():
                count += 1
            self._countryDict[state] = count        
    
        self._conn.close()
        
        # Open up connection between Pandas and SQL database independently from sqlites's database and cursor.
        engine = create_engine("sqlite:///NPS.db")
        df = pd.read_sql("SELECT longitude, latitude FROM NPStable", engine)
        
        # Calculate the mean for the longitude and latitude, then fill the "Nan" slots in the data.
        # This is because some national parks do not have the information for longitude and latitude.
        longitudeMean = df['longitude'].mean()
        latitudeMean = df['latitude'].mean()        
        self._df3 = df.fillna(df.mean()) # Is this efficient design?
        
        
    def plotCountryStats(self):  
        '''Plot number of NPS of all states across US, sorted from greatest to least'''
        xRange = np.arange(0, len(Statistics.states))
        xList = Statistics.states
        yList = list()                  
        for _, count in self._countryDict.items():
            yList.append(count)
        
        x = list()
        y = list()        
        d = dict(zip(xList, yList))
        # Sort by dictionary value (need lambda), from greatest to least
        for k,v in sorted(d.items(), key=lambda t:t[1], reverse = True): 
            x.append(k)
            y.append(v)        
        
        plt.plot(x, y, label = "state-to-state")
        plt.title("ALL STATES")
        plt.ylabel("Count") 
        plt.legend(loc = "best")
        plt.xticks(xRange,x,rotation='vertical')  
        #plt.show()
        
        
    def plotStatesStats(self,statesDict):
        """
        Plot designation stats of 1-3 states across US.
        statesDict is passed into the function, instead of being implemented
        as a class attribute, for memory efficiency.
        
        statesDict is a dict of dicts {CA: {memorial:5,trails:10,...}, NY: {beaches:7,trails:5,...}}
        """        
        # For this catplot function, it is different from other seaborn or matplotlib function, because it 
        # actually returns a plot.
        
        # Directly formatting the plot through the matplotlib plt won't work well, such as 
        # plt.title("Comparison of designations for 1-3 states",fontsize=5),
        # so I had to directly format the plot through plot.fig.suptitle(...), in order to adjust it.
        
        # I also had to return plot.fig, so the GUI function for Canvas had to be adjusted slightly differently
        # in order to account for this difference.

        #f = plt.subplots(figsize=(11,9)) # This doesn't work well, since we don't directly call matplotlib in GUI for this function.
        
        # Pass the dictionary into the Pandas dataframe
        df = pd.DataFrame(statesDict)
        
        # Based on dict1 = {0:'Park', 1:'Historic',...}, replace the 0 1 2 3 4 ... column in Pandas table
        # with the values in dict1.
        dict1 = dict(zip([i for i in range(len(Statistics.designations))],Statistics.designations))
        df = df.rename(index=dict1)

        # Add another column labeled "Designations" to Pandas for all designations
        df['Designation'] = Statistics.designations
        
        # print(df)
        # pd.melt() compresses several columns of the Pandas table in order for us to create
        # multiple barplots through catplot.
        # Link: https://stackoverflow.com/questions/38807895/seaborn-multiple-barplots/51222510
        
        # id_vars - your x axis values
        # var_names - the name of the 1 column after several columns are compressed
        # value_name - your y axis values
        
        # Here, it compresses 1-3 state columns into just 1 column
        """       AZ  CA  NY Designation           Designation States  Count
        Park       4  10   3        Park    ->  0         Park     AZ      4
        Historic   5  10  15    Historic        8     Historic     CA     10
        ...                                     ...                          """
        df = pd.melt(df, id_vars="Designation",var_name="States", value_name="Count")
        # print(df)
        # height = 6 adjusts the height of the plot
        plot = sns.catplot(x="Designation",y="Count",hue="States",data=df,kind='bar',height=6)
        
        # It is better to adjust the features through plot.fig, since we are returning the object to the GUI
        #plt.title("Comparison of designations for 1-3 states",fontsize=5) # This doesn't work well.
        
        # Adjust the title of the plot for display
        plot.fig.subplots_adjust(top=0.9)
        plot.fig.suptitle("Comparison of designations for 1-3 states")

        return plot.fig # Note the difference here that catplot requires us returning an actual plot.
        #plt.show()        


    def plotLatitudeLongitudeStats(self):
        '''Plot the latitude and longitude of each NPS in the US, and implement least regression '''
        # Call seaborn's regression plot
        plot = sns.regplot(data = self._df3, x = "longitude", y = "latitude", label="least regression line")
        plt.title("Longitude and Latitude for all National Parks in US")
        plt.legend(loc="best")
        #plt.show()


def main():
    c = Statistics()
    c.plotCountryStats()
    statesDict = {'AR':[2, 4, 1, 0, 0, 1, 1],'CA':[10, 10, 0, 7, 0, 1, 4],'IN':[2, 2, 0, 0, 0, 1, 1]}
    c.plotStatesStats(statesDict)
    c.plotLatitudeLongitudeStats()

if __name__ == "__main__":
    main()