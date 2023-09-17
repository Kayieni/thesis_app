# this file will read the areas activated (e.g. Vamvakaris or uploaded)
# it will scan the events existing in the database
# it will identify in which area each one of them exists
# it will assign the area code to the event, in the last database column
# This file has to run everytime together with the one that updates the events

# then another file for each area that is being clicked, it will filter the database and render the list of all events for this area. 

import json
import mysql.connector as mysql
from mysql.connector import Error
from shapely.geometry import Polygon, Point, shape


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

        cursor.execute('''SELECT longitude,latitude,id,of_area FROM events''')
        coordinates = cursor.fetchall()
        # print(coordinates)
        # the problem with the following is that i dont yet know which areas source is activated
        # this works for the vamvakaris one, that i have passed in the database 
        # but i cant pass in the database the data of someone random
        # cursor.execute('''SELECT id,code,area_poly,WKT FROM areas''')
        # areas = cursor.fetchall()
        # # print(areas)
        
        # # for every event (point)
        # for event in coordinates:
        #     if event[3] == "TBA":
        #         point='POINT ('+str(event[0])+" "+str(event[1]) + ')' #long/lat
        #         # print(point,"\n for: ", event[2]) #for "id"

        #         # check if it belongs to the polygons
        #         # for area in polygons:
        #         for area in areas:

        #             cursor.execute("SELECT ST_CONTAINS(ST_GeomFromText(%s),ST_GeomFromText(%s))",(area[3],point)) #area3 = WKT, point = coordinates of events
        #             # print(area[3],point)
        #             if cursor.fetchall()[0][0] == 1:
        #                 # print(polygons.index(area))    
        #                 print("area code: ", area[1])    
        #                 print("--")

        #    
        #              cursor.execute("UPDATE events SET of_area = %s WHERE id = %s", (area[1],event[2]))
        columns = [column[0] for column in cursor.description]  # Get column names


        # here will be the path for the file selected
        json_selected = {
                "features": [
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            21.23,
                            38.97
                            ],
                            [
                            21.18,
                            38.54
                            ],
                            [
                            21.65,
                            38.53
                            ],
                            [
                            22.2,
                            38.5
                            ],
                            [
                            21.8,
                            38.98
                            ],
                            [
                            21.45,
                            39
                            ],
                            [
                            21.23,
                            38.97
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-F3",
                        "id": 56,
                        "name": "Aitoloakarnania"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            22.38,
                            38.46
                            ],
                            [
                            22.4,
                            38
                            ],
                            [
                            22.7,
                            37.82
                            ],
                            [
                            23.1,
                            38.44
                            ],
                            [
                            22.82,
                            38.42
                            ],
                            [
                            22.38,
                            38.46
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-F9",
                        "id": 62,
                        "name": "Corinthiakos"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            20.85,
                            38
                            ],
                            [
                            21.22,
                            37.63
                            ],
                            [
                            22,
                            38.1
                            ],
                            [
                            21.65,
                            38.35
                            ],
                            [
                            20.85,
                            38
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-H1",
                        "id": 67,
                        "name": "Andravida"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            21.22,
                            37.63
                            ],
                            [
                            21.38,
                            37.5
                            ],
                            [
                            21.12,
                            37.32
                            ],
                            [
                            21.4,
                            37.05
                            ],
                            [
                            21.55,
                            37.15
                            ],
                            [
                            22,
                            37.35
                            ],
                            [
                            22.5,
                            37.45
                            ],
                            [
                            22,
                            38.1
                            ],
                            [
                            21.22,
                            37.63
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-H2",
                        "id": 68,
                        "name": "Kiparissiakos"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            24.75,
                            38.45
                            ],
                            [
                            24.5,
                            38.32
                            ],
                            [
                            24.7,
                            37.95
                            ],
                            [
                            23.7,
                            37.5
                            ],
                            [
                            23.45,
                            37.15
                            ],
                            [
                            24,
                            36.65
                            ],
                            [
                            24.4,
                            36.95
                            ],
                            [
                            24.8,
                            36.75
                            ],
                            [
                            25.1,
                            36.45
                            ],
                            [
                            25.5,
                            36.65
                            ],
                            [
                            26.5,
                            37.3
                            ],
                            [
                            26.5,
                            37.75
                            ],
                            [
                            25.25,
                            38.15
                            ],
                            [
                            24.75,
                            38.45
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-J1",
                        "id": 93,
                        "name": "Cyclades"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            23.45,
                            37.15
                            ],
                            [
                            23.5,
                            36.65
                            ],
                            [
                            23.5,
                            36.25
                            ],
                            [
                            25.4,
                            35.8
                            ],
                            [
                            25.4,
                            36.22
                            ],
                            [
                            25.1,
                            36.45
                            ],
                            [
                            24.8,
                            36.75
                            ],
                            [
                            24.4,
                            36.45
                            ],
                            [
                            24,
                            36.65
                            ],
                            [
                            23.45,
                            37.15
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-J2",
                        "id": 94,
                        "name": "S. Aegean 1"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            24,
                            36.65
                            ],
                            [
                            24.4,
                            36.45
                            ],
                            [
                            24.8,
                            36.75
                            ],
                            [
                            24.4,
                            36.95
                            ],
                            [
                            24,
                            36.65
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-J3",
                        "id": 95,
                        "name": "Milos"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            25.65,
                            36.45
                            ],
                            [
                            25.4,
                            36.22
                            ],
                            [
                            25.4,
                            35.8
                            ],
                            [
                            26.7,
                            35.85
                            ],
                            [
                            26.85,
                            36.45
                            ],
                            [
                            25.65,
                            36.45
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-J4",
                        "id": 96,
                        "name": "S. Aegean 2"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            25.25,
                            38.15
                            ],
                            [
                            26.5,
                            37.75
                            ],
                            [
                            27.1,
                            38.05
                            ],
                            [
                            26.4,
                            38.7
                            ],
                            [
                            26.15,
                            38.75
                            ],
                            [
                            25.25,
                            38.15
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K1",
                        "id": 97,
                        "name": "Chios"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            29.4,
                            37.15
                            ],
                            [
                            29.9,
                            36.9
                            ],
                            [
                            30.5,
                            36.7
                            ],
                            [
                            31.1,
                            36.7
                            ],
                            [
                            31.1,
                            37.95
                            ],
                            [
                            30.2,
                            37.95
                            ],
                            [
                            29.4,
                            37.15
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K10",
                        "id": 106,
                        "name": "Antalya"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            25.1,
                            36.45
                            ],
                            [
                            25.4,
                            36.22
                            ],
                            [
                            25.65,
                            36.45
                            ],
                            [
                            25.5,
                            36.65
                            ],
                            [
                            25.1,
                            36.45
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K11",
                        "id": 107,
                        "name": "Santorini"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            25.5,
                            36.65
                            ],
                            [
                            25.65,
                            36.45
                            ],
                            [
                            26.85,
                            36.45
                            ],
                            [
                            26.5,
                            37.3
                            ],
                            [
                            25.5,
                            36.65
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K12",
                        "id": 108,
                        "name": "Amorgos"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            26.5,
                            37.3
                            ],
                            [
                            26.85,
                            36.45
                            ],
                            [
                            27.2,
                            36.5
                            ],
                            [
                            27.5,
                            36.6
                            ],
                            [
                            27.4,
                            37.28
                            ],
                            [
                            26.5,
                            37.3
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K13",
                        "id": 109,
                        "name": "Kos"
                    },
                    "type": "Feature"
                    },
                    {
                    "geometry": {
                        "coordinates": [
                        [
                            [
                            27.4,
                            37.28
                            ],
                            [
                            27.5,
                            36.6
                            ],
                            [
                            28.75,
                            37
                            ],
                            [
                            28.75,
                            37.2
                            ],
                            [
                            27.4,
                            37.28
                            ]
                        ]
                        ],
                        "type": "Polygon"
                    },
                    "properties": {
                        "code": "N-K14",
                        "id": 110,
                        "name": "Bodrum"
                    },
                    "type": "Feature"
                    }
                ],
                "type": "FeatureCollection"
            }

        # print(json_selected)
        # print(json_selected['features'])
        # json.stringify(json_selected)
        area_belong = ""
        for row in coordinates:
            # print("\n\n", row)
            point = Point(row[0],row[1])
            # print(point)
            for feature in json_selected['features']:
                # print(feature)
                # print(feature['geometry'])
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    # event_dict = dict(zip(columns, row))  # Create a dictionary for each row
                    area_belong = feature['properties']['code']
                    print(area_belong)

                else:
                    continue
            print("This event ("+ row[2] +") belongs to the :", area_belong)
    

        db.commit()

except Error as e:
    print("Error while connecting to MySQL. \n", e)
