structure
_________

1. static
    a. data
        i.  areas-vamv.json # geojson file crated in views.py/vamv-geojson
        ii. thesis (1).sql  # a backup of the database
    b. images
        i.  samos20.png     # favicon of web application -> the FM of samos 2020 earthquake
    c. style.css
2. templates
    a. list.html            
    b. map.html             # the main map, loaded in the index (/) of the app
3. app.py
        # initiate mysql connection / configurations and set up the server, listening to the port 8000
5. coordinates.py
        # a python file that parses the txt copied and pasted by the paper (διαδακτορική Διατριβή Βαμβακάρης) Table 3-7, page 143-156
6. cords_db.py
        # This file takes the coordinates of the Vamvakakis PhD Research and pass it into the database. 
        # Also it recognises in which of those areas does each of the current earthquakes belong.
7. cords.csv
        # csv created after the txt parsing of the vamv phd
8. cords.txt
        # the file with the coppied and pasted areas by the Vamvakaris phd thesis
9. edit.py
        # similar to main.py, better version
        # This file will read the map.html file
        # It will try to gather only the info needed
        # Export then into a readable file
10. gisola.html
        # the html of the gisola to use as an example
11. main.py
        # This file is reading the url and is creating a file named list.html which includes all the info provided by the list view of the gisola software

15. views.py
        # in this file all the routes are created. 
        # here is also being created the geojson file from the vamvakaris polygons to be used in leaflet