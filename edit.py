# This file will read the map.html file
# It will try to gather only the info needed
# Export then into a readable file
from flask import Flask
from flask import request, jsonify, render_template, redirect
import os
import requests
from bs4 import BeautifulSoup
from obs import read_events, Catalog, UTCDateTime
from obspy.core.event import read_events
import xml.etree.ElementTree as ET
import mysql.connector as mysql
from mysql.connector import Error

# only 2023 for now
# this will change
# how to make it syncronus

# Send a GET request to the website
url = 'https://bbnet.gein.noa.gr/gisola/realtime/2023/'
response = requests.get(url, verify=False)
print('ok request with code:' +str(response.status_code))

# parse the html of the url above
soup = BeautifulSoup(response.content, 'html.parser')

# access the table with the list of earthquakes
table = soup.find('table')

# print(len(table))
# print(table)

# access the link of each element of the list
# or find the pattern and extract all the data

# for each row of the table of the url provided
# (each row contains one earthquake)
for row in table.find_all('tr'):
    # check if a link exists, to go to the details
    if row.find('a'):
        # get the href linked
        path = row.find('a')['href']
        # grap the first part only (not the /index.html) to go to the directory
        link = path.rsplit('/', 1)[0]
        # join everything to create the path for the xml of the QuakeML file
        code = path.split('/', 1)[0]
        quakefile = url+'/'+link+'/event.xml'
        # print(row.text, quakefile)

        # fetch the XML data from the URL
        response = requests.get(quakefile, verify=False)
        file = code+'.xml'

        with open(file, 'wb') as f:
            filecont = f.write(response.content)

####### __________________ ??? _______________
        data = {'data': []}
        try:
            # print(read_events(file))
            # to see all the event's details
            # e.g. amount of event descriptions, about of focal machanisms, amount of picks, origins, and magnitudes
            # e.g.: 
            # 1 Event(s) in Catalog:
            # 2023-01-04T20:03:55.762778Z | +38.713,  +23.696 | 4.06 MLh | automatic

            for evt in read_events(file):
                # for event origins
                try:
                    # the event details will be printed
                    # print(evt)
                    # to get the preferred origin of the data
                    # meaning the most ~accurate
                    org = evt.preferred_origin()
                    # print("org",org)
                    # print("evt origins:" , evt.origins)
                    # print('lambda: ' , lambda o: o.creation_info.creation_time)
                    # print("-1: ", evt.origins[-1])
                    if not org: raise

                # which origin to select
                except:
                    try:
                        # if more than one, sort based in creation time
                        org = sorted(evt.origins, key=lambda o: o.creation_info.creation_time)[-1]
                    except:
                        # if only one, select the last
                        org = evt.origins[-1]

                # for moment tensors
                try:
                    # get moment tensor
                    fm = evt.preferred_focal_mechanism()

                    # get origin of moment tensor (mt)
                    cent_org_id = fm.moment_tensor.derived_origin_id

                    # get magnitude associated with the mt's origin
                    cent_mag = [m for m in evt.magnitudes if m.origin_id == org.resource_id][0]

                except:
                    continue

                d = {
                    "time": str(org.time).split('.')[0],
                    "Mw": cent_mag.mag,
                    "longitude": org.longitude,
                    "latitude": org.latitude,
                    "depth": org.depth / 1000,
                    "id": str("{:.2e}".format(fm.moment_tensor.scalar_moment)),
                    "try": str(evt.resource_id).split("geofon/")[1],
                    "mt": str(org.time).split('.')[0] + "_" + str(evt.resource_id).split("geofon/")[1],
                    "mwa": str(org.time).split('-')[0] + '_' + str(org.time).split('-')[1] + "_" +
                            str(evt.resource_id).split("geofon/")[1] + "_" + str(cent_mag.mag),
                    "link": quakefile,
                }
                if org.depth > 1000000:
                    continue
                if org.depth_errors.uncertainty:
                    if org.depth_errors.uncertainty > 100000:
                        continue

                data["data"].append(d)
                # print("uncertainty:" , org.depth_errors.uncertainty)
                print(data)
                print("\n ------------------------------------------------- \n")

                            
                # connect database
                    
                try:
                    db = mysql.connect(
                        host='localhost',
                        user='root',
                        database = 'thesis',
                        passwd='',
                    )

                    if db.is_connected():
                        cursor = db.cursor(buffered=True) #like a little robot that will do commands for you
                        # cursor = db.cursor(buffered=True)
                        # cursor.execute("CREATE DATABASE IF NOT EXISTS thesis")
                        # print("irisDB database is created")
                        # cursor.execute("select * from areas")

                        # to check in which area it belongs
                        # cursor.execute('''SELECT * FROM coordinates WHERE longitude''')

                        cursor.execute('''INSERT INTO events VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                            (data["data"][0]["time"], 
                            data["data"][0]["Mw"],
                            data["data"][0]["longitude"],
                            data["data"][0]["latitude"],
                            data["data"][0]["depth"],
                            data["data"][0]["id"],
                            data["data"][0]["try"],
                            data["data"][0]["mt"],
                            data["data"][0]["mwa"],
                            data["data"][0]["link"])                         
                        )                
                
                        db.commit()

                except Error as e:
                    print("Error while connecting to MySQL. \n", e)



        except:
            pass

        os.remove(file)
        # jsonify(data)

        # print(d)

    else:
        print(row.text)



