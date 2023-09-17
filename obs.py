# we get the real time seismic data from fdsn server ORFEUS
# every time it only reads the new events (from the last one available in the database) and updates the database
# it can also work for the search of older events
# 
# Here the beachballs are created too


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
import matplotlib.pyplot as plt
import os
from obspy.imaging.beachball import beach, beachball
from mysql.connector import Error

# to draw the beachball for each
def beachball(fm, id,mw, d):
    
    if(d<10):
        facecolor = "b"
    elif(d<30):
        facecolor = "g"
    elif(d<60):
        facecolor = "yellow"
    elif(d<100):
        facecolor = "orange"
    else:
        facecolor = "r"



    
    """
    Plotting the focal mechanism
    """
    filepath=os.path.join("./static/beachballs", ('beachball_'+ id +'.png'))

    # radius of the ball
    radius = 100

    fig = plt.figure(figsize=(mw/10,mw/10))
    ax = fig.add_subplot(111)

    # Moment Tensor
    try:
        nofill=True
        focal1 = beach([fm.moment_tensor.tensor.m_rr,fm.moment_tensor.tensor.m_tt,\
        fm.moment_tensor.tensor.m_pp,fm.moment_tensor.tensor.m_rt,\
        fm.moment_tensor.tensor.m_rp,fm.moment_tensor.tensor.m_tp], xy=(0.0,0.0), \
        width=2*radius,axes=None,alpha=1, facecolor=facecolor, zorder=1)

        ax.add_collection(focal1)

    except:
        # fall back to dc only with color
        nofill=False
    # Planes
    focal2 = beach([fm.nodal_planes.nodal_plane_1.strike,\
    fm.nodal_planes.nodal_plane_1.dip,fm.nodal_planes.nodal_plane_1.rake], \
    nofill=nofill, facecolor=facecolor, xy=(0.0,0.0),axes=None,width=2*radius,zorder=2)

    ax.add_collection(focal2)

    ax.autoscale_view(tight=False, scalex=True, scaley=True)
    
    # plot the axis
    ax.axison=False
    plt.axis('scaled')
    ax.set_aspect(1)

    fig.savefig(filepath, transparent=True)
    # plt.show()




# το obspy με client == ΝΟΑ δεν τρεχει, και βγαζει συνεχεια στατους 413: Request would result in too much data. Denied by the datacenter. Split the request in smaller parts
# Άρα θα κάνω ξεχωριστό request όπως στη διπλωματική της Δήμητρας


# βλεπω ολους τους διαθεσιμους clients
from obspy.clients.fdsn.header import URL_MAPPINGS
for key in sorted(URL_MAPPINGS.keys()):
    print("{0:<11} {1}".format(key,  URL_MAPPINGS[key]))  

# NOA is the catalog service we want for Greece FDSN Service
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
        r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?'+starttime+'includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404')
        # r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404')

        # for older events
        # r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?'+endtime+'includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404')
        
        with open(filename,'wb') as f:
            f.write(r.content)

        counter = 0
        data={'data':[]}
        print("data ok")

        try:
            prev_time = 0
            for evt in read_events(filename):
                if(evt.focal_mechanisms):
                    
                    org = evt.preferred_origin() or evt.origins[0]
                    print("org ok")
                    if(str(org.time).rsplit(":",1)[0]  == str(prev_time).rsplit(":",1)[0] ):
                        continue
                    else:
                        print("---------\nEvent id: " + str(evt.resource_id).split('/')[-1] + "\nTime: " +  str(org.time) )
                        if (evt.preferred_focal_mechanism_id):
                            fm = list(filter(lambda x: x.resource_id == evt.preferred_focal_mechanism_id,evt.focal_mechanisms))[0]
                        else:
                            fm = evt.focal_mechanisms[0]
                        
                    # try:
                    #     # fm = evt.preferred_focal_mechanism() or evt.focal_mechanisms[0]
                    #     fm = list(filter(lambda x: x.resource_id == evt.preferred_focal_mechanism_id,evt.focal_mechanisms))[0] or evt.focal_mechanisms[0]
                    # except:
                    #     continue
                        print("fm ok")

                        # get magnitude associated with the mt's origin
                        cent_mag = [m for m in evt.magnitudes if m.origin_id == org.resource_id]
                        if cent_mag:
                            cent_mag = cent_mag[0]
                        else:
                            continue  # Skip the iteration if cent_mag is empty
                        
                        print("cent mag ok")
                        
                        tensor = fm.moment_tensor.tensor
                        print("tensor ok")

                        moment_list = [tensor.m_rr, tensor.m_tt, tensor.m_pp,
                        tensor.m_rt, tensor.m_rp, tensor.m_tp]
                        print("list ok")

                        mt_list_db = "/".join([str(elem) for elem in moment_list])
                        print("db list ok")

                        event_id = str(evt.resource_id).split('/')[-1]
                        mw = round(cent_mag.mag,1)
                        depth = round(org.depth/1000,1)
                        # create the beachball to the ./static/beachballs/beachball_[event_id].png
                        beachball(fm, event_id, mw ,depth)
                        print(event_id)

                        d = {
                            "time" : str(org.time),
                            "Mw" : mw,
                            "longitude": round(org.longitude,4),
                            "latitude": round(org.latitude,4),
                            "depth": depth,
                            "id": event_id,
                            "strike": fm.nodal_planes.nodal_plane_1.strike,
                            "dip": fm.nodal_planes.nodal_plane_1.dip,
                            "rake": fm.nodal_planes.nodal_plane_1.rake,
                            "mtlist": mt_list_db

                        }
                        print("d ok")
                            
                        data["data"].append(d)

                        print(d)
                        
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
                                        d["strike"],
                                        d["dip"],
                                        d["rake"],
                                        d["mtlist"],
                                        "TBA"
                                        )
                                    )

                            db.commit()
                            print("\n ------------------------------------------------- \n")       

                        except Error as e:
                            print("Error while inserting into MySQL. \n", e)

                        counter+=1
                        # beachball(focmec)
                        prev_time = org.time

                else:
                    print("======================================\nEvent doesnt have Focal Mechanisms\nEvent id: " + str(evt.resource_id).split('/')[-1] + "\nTime: " + str(org.time)+"\n========================================")
                    continue 
                
            print(counter)
        except Exception as e:
            print("Error while reading events:",e)
            traceback.print_exc()

except Error as e:
    print("Error while connecting to MySQL. \n", e)

db.close()