# we get the real time seismic data from fdsn server
# every time it only reads the new events (from the last one available in the database) and updates the database
# it can also work for the search of older events


import traceback
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException
from obspy.core.event.event import Event
from obspy.core.event.origin import Origin
from obspy.core.event.magnitude import Magnitude
from obspy.core.event.catalog import Catalog
from obspy.core.event import read_events
import requests
from geojson import Point, Polygon, Feature
import mysql.connector as mysql
from mysql.connector import Error

# το obspy με client == ΝΟΑ δεν τρεχει, και βγαζει συνεχεια στατους 413: Request would result in too much data. Denied by the datacenter. Split the request in smaller parts
# Άρα θα κάνω ξεχωριστό request όπως στη διπλωματική της Δήμητρας


# βλεπω ολους τους διαθεσιμους clients
from obspy.clients.fdsn.header import URL_MAPPINGS
for key in sorted(URL_MAPPINGS.keys()):
    print("{0:<11} {1}".format(key,  URL_MAPPINGS[key]))  

# NOA is the catalog service we want for Greece
client = Client("NOA")

    # r = client.get_events(maxlatitude = 43,minlatitude=33,minlongitude=18, maxlongitude=31)
try:
    # connect database
    db = mysql.connect(
        host='localhost',
        user='root',
        database = 'thesis',
        passwd='',
    )

    if db.is_connected():
        cursor = db.cursor(buffered=True) #like a little robot that will do commands for you
        # for all the events after the last which exists in the database
        cursor.execute('''SELECT IFNULL(MAX(time), "") FROM events''')
        maxtime = str(cursor.fetchall()[0][0])
        print(maxtime)
        # for all the events before the first which exists in the database
        cursor.execute('''SELECT IFNULL(MIN(time), "") FROM events''')
        mintime = str(cursor.fetchall()[0][0])
        print(mintime)

        # for newer events
        starttime = ""
        endtime = ""
        if(maxtime==""):
            starttime = ""
        else:
            starttime = 'starttime='+maxtime.split('.')[0]+'T00%3A00%3A00&'
        
        # for older events
        if(mintime==""):
            endtime = ""
        else:
            endtime = 'endtime='+mintime.split('.')[0]+'T00%3A00%3A00&'

        filename = "obspy.xml"
    
        # for new events
        r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?'+starttime+'includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&nodata=404')

        # for older events
        # r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?'+endtime+'includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&nodata=404')
        
        with open(filename,'wb') as f:
            f.write(r.content)

        counter = 0
        data={'data':[]}
        try:
            for evt in read_events(filename):
                counter+=1
                print(counter)
                try:
                    org=evt.preferred_origin()
                    if not org: raise
                except:
                    try:
                        org=sorted(evt.origins, key=lambda o: o.creation_info.creation_time)[-1]
                    except:
                        org=evt.origins[-1]

                try:
                    # get moment tensor
                    fm=evt.preferred_focal_mechanism()
                    # print(fm.moment_tensor)
                    print(org)
                    print(org.latitude)
                    print(org.longitude)

                    # get origin of moment tensor (mt)
                    # cent_org_id=fm.moment_tensor.derived_origin_id

                    # get magnitude associated with the mt's origin
                    cent_mag=[m for m in evt.magnitudes if m.origin_id==org.resource_id][0]
                    # cent_mag = [m for m in evt.magnitudes if m.origin_id == org.resource_id]
                    # if cent_mag:
                    #     cent_mag = cent_mag[0]
                    # else:
                    #     continue  # Skip the iteration if cent_mag is empty

                
                except:
                    continue

                d = {
                    "time" : str(org.time),
                    "Mw" : round(cent_mag.mag,1),
                    "longitude": round(org.longitude,4),
                    "latitude": round(org.latitude,4),
                    "depth": round(org.depth/1000,0),
                    # "id": str("{:.2e}".format(fm.moment_tensor.scalar_moment)),
                    "id": str(org.resource_id),
                    # "try": str(evt.resource_id).split("geofon/")[1],
                    "try": str(evt.resource_id),
                    "mt" : str(org.time).split('.')[0]+"_"+str(evt.resource_id),
                    "mwa" : str(org.time).split('-')[0]+'_'+str(org.time)+"_"+str(evt.resource_id)+"_"+str(round(cent_mag.mag,1)),
                    "link" : "N/A"
                    }
                if org.depth > 1000000:
                    continue
                if org.depth_errors.uncertainty :
                    if org.depth_errors.uncertainty > 100000 :
                        continue
                    
                data["data"].append(d)
                print(org.depth_errors.uncertainty)
                # print("--------")
                # print(data["data"][0]["time"])
                print(d)
                # connect database
                # cursor = db.cursor(buffered=True) #like a little robot that will do commands for you
                print("--------")

                # connect database
                
            
                # Insert data into the database
                try:
                    cursor.execute('''INSERT IGNORE INTO events VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                            (   d["time"],
                                d["Mw"],
                                d["longitude"],
                                d["latitude"],
                                d["depth"],
                                d["id"],
                                d["try"],
                                d["mt"],
                                d["mwa"],
                                d["link"],
                                "TBA"
                                )
                            )

                    db.commit()
                    print("\n ------------------------------------------------- \n")       

                except Error as e:
                    print("Error while inserting into MySQL. \n", e)

        except Exception as e:
            print("Error while reading events:")
            traceback.print_exc()

except Error as e:
    print("Error while connecting to MySQL. \n", e)

db.close()