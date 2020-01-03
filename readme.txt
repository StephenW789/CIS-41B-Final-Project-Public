CIS 41B Final Project – National Park Service

										Fall 2019
Jasmine Wong & Stephen Wong 


This project has total 6 files. 
* 4 source code files: : the private_API_key.py, the backend_oneCursorPerThread.py, the GUI.py, and the Statistics.py.
* 1 database file: NPS.db
* 1 readme.doc file: the file you’re reading now.


How to run the project:
1. 1.	Create the private_API_key.py file as follows:
		import os
		os.environ["API_Key"] = "Your API key here…”

2. Run backend_oneCursorPerThread.py, and it generates NPS.db
3. Run GUI.py, a MainWindow shows and users have 5 choices.

	a) Click “Menubutton” brings down a pull-down menu. Users can choose one state by 		clicking on it. Once you select a state, be sure to click the ‘OK’ button at the 		bottom of the MainWindow to proceed. Then, a DialogWindow will appear with all 	national parks for that state. Users can select up to one national park, and by 		clicking ‘OK’, detailed information about the park will be shown in a Display 	Window.  Finally, a “Save” button will pop up, and the detailed info about that 	specific park will be saved within the file “National Parks.txt” under the user’s 	chosen directory.

	b) Click “byDesignation” brings down a list of designations. Users can choose up to 	one designation. Clicking ‘OK’ will display all National Parks in the US with that 	designation.

	c) Click “byCountry” will open a new window with a plot for the number of National 	Parks for every US state, listed in sorted descending order.

	d) Click “byStats” will open a 5 * 10 checkbuttons selection window, where the user 	can select 1-3 states. 
	Once the user clicks ‘OK’ at the bottom of the selection window, multiple barplots 	will appear for the states.

	e) Click “byLatitudeandLongitude” will open a scatterplot for the longitude and 	latitude for each National Park in the US, as well as display a least regression 	line.
