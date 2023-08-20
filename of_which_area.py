# this file will read the areas activated (e.g. Vamvakaris or uploaded)
# it will scan the events existing in the database
# it will identify in which area each one of them exists
# it will assign the area code to the event, in the last database column
# This file has to run everytime together with the one that updates the events

# then another file for each area that is being clicked, it will filter the database and render the list of all events for this area. 

import mysql.connector as mysql
from mysql.connector import Error

print("1---")

try:
    print("2---")

    # connect with database
    db = mysql.connect(
        host='localhost',
        user='root',
        database = 'thesis',
        passwd='',
    )

    if db.is_connected():
        print("it runs")
        cursor = db.cursor(buffered=True) #like a little robot that will do commands for you

        cursor.execute('''SELECT longitude,latitude,try,of_area FROM events''')
        coordinates = cursor.fetchall()

        # the problem with the following is that i dont yet know which areas source is activated
        # this works for the vamvakaris one, that i have passed in the database 
        # but i cant pass in the database the data of someone random
        cursor.execute('''SELECT id,code,area_poly,WKT FROM areas''')
        areas = cursor.fetchall()
        
        # for every event (point)
        for event in coordinates:
            if event[3] == "TBA":
                point='POINT ('+str(event[0])+" "+str(event[1]) + ')' #long/lat
                print(point,"\n for: ", event[2]) #for "try"

                # check if it belongs to the polygons
                # for area in polygons:
                for area in areas:

                    cursor.execute("SELECT ST_CONTAINS(ST_GeomFromText(%s),ST_GeomFromText(%s))",(area[3],point)) #area3 = WKT, point = coordinates of events
                    if cursor.fetchall()[0][0] == 1:
                        # print(polygons.index(area))    
                        print("area code: ", area[1])    
                        print("--")

                        cursor.execute("UPDATE events SET of_area = %s WHERE try = %s", (area[1],event[2]))


        db.commit()

except Error as e:
    print("Error while connecting to MySQL. \n", e)
