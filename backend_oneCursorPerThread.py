'''
CIS 41B Final Project, Fall 2019
Written by Jasmine Wang and Stephen Wong

This project has 3 files, the backend_oneCursorPerThread.py, the GUI.py, and the Statistics.py.

This is the backend_oneCursorPerThread.py file. It makes the API calls for the National Parks for all 50 states
using threading, one thread per state. Due to the rate limit of the website, we set a semaphore to 25 threads for 
controlling how many threads can concurrently accessthe website.

We open one DB connection to the SQL database. During the threading portion, each thread has one cursor (for a
total of 50 cursors). The cursors are local variables, and will be terminated once the threading function has ended.
The portion where the threads insert the data into the SQL database is not controlled by the semaphore.

We chose one cursor per thread to process data immediately once w fetch it over a threading queue to eliminate the middleman(queue), which improves performance.
For detailed data and performance timing, please see the end of the file.

This file covers webAPI, threading, and database modules.
'''

import requests
import json
import threading
import time
import sqlite3
import os
import private_API_key # Create a private python file that houses the environment variable

class FindData():

    ''' The followings are class variables '''
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]  
   
    root = "https://developer.nps.gov/api/v1/parks?"
    
    # Either manually set the API key (Fill in the key within the quotations)
    #API_Key = "" 
    
    # or
    
    # Obtain the API key from the environmental variable
    API_Key = os.environ.get("API_Key")
    
    # For stateCode, you can't grab data for all 50 states. So, 
    # you create 50 threads for 50 states.
    dataStr1 = "stateCode=" # stateCode is ex. 'CA' - California
    dataStr2 = "&api_key="    
    # Format: {"total":"33","data":[{park1 data},{park2 data}]}

    # Only needed for extra search criteria - such as searching by Calendar
    dataStr3 = "parkCode="
    dataStr4 = "&fields=addresses"
        
    def __init__(self):
        self.openDBConnection()
        self.createTable()
        
        # The semaphore limits 25 threads max for the API search, otherwise we will
        # trigger too many API requests for the website
        self._semaphore = threading.Semaphore(25) 
    
        threads = []
        for state in FindData.states:
            t = threading.Thread(target=self._getAllData, args=(state,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
            
        self._conn.commit()
    
    def _getAllData(self,state):
        '''_getAllData makes the API request and writes to the SQL database '''
        
        # The semaphore block is only needed for preventing too many calls for the API,
        # It is not needed for the SQL table writing in self.insertIntoTable(page.json()).
        with self._semaphore:
            # Defensive Programming
            try:
                page = requests.get(FindData.root + FindData.dataStr1 + state + FindData.dataStr2 + FindData.API_Key)
                page.raise_for_status()
                
            except requests.exceptions.HTTPError as e:
                print("HTTP Error: ", e)
                raise SystemExit
            except requests.exceptions.ConnectionError as e:
                print("Error Connecting: ", e)
                raise SystemExit
            except requests.exceptions.RequestException as e:
                print("Request exception: ", e)
                raise SystemExit
       
        self.insertIntoTable(page.json())
        
        
    def insertIntoTable(self, jsondata):
        '''insertIntoTable inserts the python data structure from API call
        into the SQL database'''
        _resultDict = jsondata
        stateTotal = int(_resultDict["total"])

        for i in range(stateTotal):
            temp = _resultDict["data"][i]["latLong"]
            if temp != "":
                temps = temp.split(", ")
                latitude = float(temps[0].split(":")[1])
                longitude = float(temps[1].split(":")[1]) 
            else:
                latitude = None
                longitude = None
                                   
            insertStatement = "INSERT INTO NPStable Values(?,?,?,?,?,?,?)"
            insertValues = (_resultDict["data"][i]["fullName"], _resultDict["data"][i]["states"], _resultDict["data"][i]["designation"], _resultDict["data"][i]["description"], _resultDict["data"][i]["directionsUrl"], longitude, latitude)
            cur = self._conn.cursor()
            cur.execute(insertStatement, insertValues)
        
     
    def openDBConnection(self):
        '''openDBConnection connects to the NPS SQL database '''
        self._conn = sqlite3.connect("NPS.db", check_same_thread = False)
        

    def createTable(self):
        '''createTable creates the SQL database '''
        dropTableStatement = "DROP TABLE IF EXISTS NPStable"
        createTableStatement = """CREATE TABLE NPStable(
                                 name TEXT UNIQUE ON CONFLICT IGNORE,
                                 states TEXT,
                                 designation TEXT,
                                 description TEXT,
                                 directionsUrl TEXT,
                                 longitude REAL, 
                                 latitude REAL)"""
        
        self._cur = self._conn.cursor()
        self._cur.execute(dropTableStatement)
        self._cur.execute(createTableStatement)
        
        
    def closeDBConnection(self):
        '''Closes the connection to the SQL table '''
        self._conn.close()
 

def main():
    start = time.time()
    finddata = FindData()
    print("Total time is ", time.time() - start)
    finddata.closeDBConnection()
    print("After closing DB...")
   
if __name__ == "__main__":
    main()

# Should we create another class for saving the data?
# Is this a good design?
# For the 50 threads, it takes around 70 seconds to load. Is this a good design?
# How can we speed it up?
# Dad mentioned: shard, hash to split data more evenly across threads.
# We encountered exceed rate limit for the earlier API fetch. Does it remove some of our data?



# We choose the DB one cursor per thread method over the Queue method because of performace, based on the following stats. 
# Using DB one cursor per thread method:
# the following Total time covers thread of fetching data + insert data into db 

# Split the page.json() into two steps in an attempt to fix the IndexOutOfBounds error in in the loop
# 1st trial, Total timeis around 66.83663201332092s, number of record in DBBrowser: 461
# 2rd, Total time is  86.49825310707092 with print statement
# 3rd Total time is  140.73402500152588 with print statement, number of record in DBBrowser: 450
 

# Removed self from _resultDict - since we always had missing records in our database
# Now, all variables in the threading functions are local.
# 4rd Total time is  66.66297483444214 with print statement, number of record in DBBrowser: 461
# 5th Total time is  82.1301338672638 with print statement, number of record in DBBrowser: 461
# 6th Total time is  67.4828200340271 without print statement, number of record in DBBrowser: 461

# Combined the page.json() back into one step, yet no IndexOutOfBounds error thrown.
# Still has 461 records in SQL database
# 7th Total time is  68.21680307388306 without print statement, number of record in DBBrowser: 461

# Using the Queue method:
# Always had 461 records in the SQL database

# 1st Trial: around 143 seconds
# 2nd Trial: Total elapsed time: 103.302750s
# 3rd Trial: Total elapsed time: 107.390782s
# 4th Trial: Total elapsed time: 118.023226s
# 5th Trial: Total elapsed time: 89.742671s