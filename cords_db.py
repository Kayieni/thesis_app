# ========================================================
# This file takes the coordinates of the Vamvakakis PhD Research and pass it into the database. 
# Also it recognises in which of those areas does each of the current earthquakes belong.

# bugs to be fixed:
# - [fixed] 1,6,10 code is only the first character, but the are also the only ones to accept the poly
# - the polys come in a bytearray like: which needs to be decoded. So thats why o stroe the WKT
#   bytearray(b'\x00\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00@E@fffff\xe61@\xcd\xcc\xcc\xcc\xcc\xccD@fffff&3@\x00\x00\x00\x00\x00\xe0D@\xcd\xcc\xcc\xcc\xcc\xcc3@33333\x13E@33333\xb33@ffffffE@\x00\x00\x00\x00\x00\x802@\x00\x00\x00\x00\x00@E@fffff\xe61@'
#   source: https://dev.mysql.com/doc/refman/8.0/en/gis-data-formats.html#gis-wkb-format
# ========================================================


import mysql.connector as mysql
from mysql.connector import Error
import pandas as pd
# from shapely.geometry import Polygon
# import shapely.wkt

# read the csv with the coordinates created
areas = pd.read_csv('./cords.csv',index_col=False)
# create a pandas dataframe in order to print the result and search the rows one by one
df = pd.DataFrame(areas)

try:
    # connect with database
    db = mysql.connect(
        host='localhost',
        user='root',
        database = 'thesis',
        passwd='',
    )

    if db.is_connected():
        cursor = db.cursor(buffered=True) #like a little robot that will do commands for you

        # initiate variables to be used to hold values for each area
        id = ""
        code = "" 
        name = ""
        pap = ""
        moun = ""
        eq = ""
        mmax = ""
        first = "" # to same the first coords
        latlong = [] # a table with coordinates of an area. It has 113 possitions, as many as the areas
        poly = "" # the coordinates of the polygon
        polygons = []
        counter = 0  # counter is the number of areas
        code_tmp = ""

        # maybe a number of rows in one area should be used too.

        # for each row of the csv of areas
        for row in df.itertuples():
            # each row has some data. There are some rows with only coordinates that specify the area of the last code seen.
            # So if the code is not the same, that means we changes area. 
            # If its the same that means we still look at the area's coordinates.
            if (row.code != code_tmp):
                # to start from area 1, cause there is no area 0
                if(counter>0):
                    # counter -1 bc counter starts from 1 but the first table element we want is in possition 0
                    latlong[counter-1] = latlong[counter-1] + "," + first

                    poly = "POLYGON((" + str(latlong[counter-1]) + "))"
                    polygons.append(poly)

                    # insert to database
                    cursor.execute("INSERT IGNORE INTO areas(id, code, name, mmax_PAP, mmax_MOUN, mmax_EQ, mmax) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (id[0], code_tmp, name[0], pap[0], moun[0], eq[0], mmax)
                    )

                    cursor.execute("UPDATE areas SET area_poly = ST_GeomFromText(%s), WKT = %s WHERE id=%s", (poly, poly, id[0]))

                counter+=1
                code_tmp = row.code

                
            if (row.code == code_tmp):
                # αν εχουμε ιδιους κωδικους κραταμε της πρωτης γραμμης, και στο πολυγωνο βάζουμε όλες τις υπολοιπες.
                # POLYGON((-114.018522 46.855932 , -113.997591 46.856030 , -113.997447 46.848626 , -114.018161 46.848824 , -114.018522 46.855932 ))
                if (row.id!=" "):
                    id = row.id, 
                    code = row.code, 
                    name = row.name, 
                    pap = row.pap, 
                    moun = row.moun,
                    eq = row.eq, 
                    mmax = row.mmax
                    print("\n======================= ",counter, " ========================= ")

                    # to save the first coords and close the polygon
                    first = str(row.lat) + " " + str(row.long)

                    latlong.append(str(row.lat) + " " + str(row.long))
                    # print(latlong)
                    cursor.execute('''INSERT INTO coordinates(area_code, latitude, longitude) VALUES (%s,%s,%s)''',
                        (row.code, row.lat, row.long)                         
                    )
                    

                if (row.id==" "):
                    latlong[counter-1] = latlong[counter-1] + "," + str(row.lat) + " " + str(row.long)
                    # print(latlong)
                    cursor.execute('''INSERT INTO coordinates(area_code, latitude, longitude) VALUES (%s,%s,%s)''',
                        (row.code, row.lat, row.long)                         
                    )
        

        print("----------------------------------------")
        # for the last iteration   
        # counter -1 bc counter starts from 1 but the first table element we want is in possition 0
        latlong[counter-1] = latlong[counter-1] + "," + first
        poly = "POLYGON((" + str(latlong[counter-1]) + "))"
        polygons.append(poly)

        # insert to database
        cursor.execute("INSERT IGNORE INTO areas(id, code, name, mmax_PAP, mmax_MOUN, mmax_EQ, mmax) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (id[0], code_tmp, name[0], pap[0], moun[0], eq[0], mmax)
        )

        cursor.execute("UPDATE areas SET area_poly = ST_GeomFromText(%s), WKT = %s WHERE id=%s", (poly, poly, id[0]))


        db.commit()
        print("--------")

        cursor.execute('''SELECT longitude,latitude,try FROM events''')
        coordinates = cursor.fetchall()

        cursor.execute('''SELECT id,code,area_poly,WKT FROM areas''')
        areas = cursor.fetchall()
        
        # for every event (point)
        for event in coordinates:
            point='POINT ('+str(event[1])+" "+str(event[0]) + ')'
            print(point,"\n for: ", event[2])

            # check if it belongs to the polygons
            # for area in polygons:
            for area in areas:

                cursor.execute("SELECT ST_CONTAINS(ST_GeomFromText(%s),ST_GeomFromText(%s))",(area[3],point)) #area3 = area_poly, point = coordinates of events
                if cursor.fetchall()[0][0] == 1:
                    # print(polygons.index(area))    
                    print("area code: ", area[1])    
                    print("--")

                    cursor.execute("UPDATE events SET of_area = %s WHERE try = %s ", (area[1],event[2]))


        db.commit()



except Error as e:
    print("Error while connecting to MySQL. \n", e)

# Comments:
# The final excedution for all the 620 inserts is very time consuming. 
# Reading the csv file does not need a lot of time.

