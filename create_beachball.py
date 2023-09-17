
import mysql.connector as mysql
import matplotlib.pyplot as plt
import os
import pandas as pd
from obspy.imaging.beachball import beach

import requests
import json 

# to draw the beachball for each
def average_mt(json):
    # i will have as input the json of the events in the area selected/drawed

    listofMT = []
    for event in json:
        id = json.id
        d = json.depth
        mw = json.mw
        strike = json.strike
        dip = json.dip
        rake = json.rake
        mt_list_db = json.mtlist
        areacode = json.of_area

        moment_list = mt_list_db.split('/')
        listofMT.append(moment_list)




    # if(d<10):
    #     facecolor = "b"
    # elif(d<30):
    #     facecolor = "g"
    # elif(d<60):
    #     facecolor = "yellow"
    # elif(d<100):
    #     facecolor = "orange"
    # else:
        facecolor = "r"

    """
    Plotting the focal mechanism
    """
    filepath=os.path.join("./static/beachballs", ('beachball_'+ areacode +'.png'))

    # calculating the average of moment list
    df = pd.DataFrame(listofMT)
    # print(df)
    df.mean()
    mesosmt = list(df.mean())

    # radius of the ball
    radius = 100

    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)




    # Average Moment Tensor
    # try:
    nofill=True
    focal1 = beach(mesosmt, xy=(0.0,0.0), \
    width=2*radius,axes=None,alpha=1, facecolor='r', zorder=1)

    ax.add_collection(focal1)

    # except:
    #     # fall back to dc only with color
    #     nofill=False
    # # Planes
    # focal2 = beach([strike,dip,rake], \
    # nofill=nofill, facecolor=facecolor, xy=(0.0,0.0),axes=None,width=2*radius,zorder=2)

    # ax.add_collection(focal2)

    ax.autoscale_view(tight=False, scalex=True, scaley=True)
    
    # plot the axis
    ax.axison=False
    plt.axis('scaled')
    ax.set_aspect(1)

    fig.savefig(filepath, transparent=True)
    # plt.show()
    

res = requests.get('localhost:8000/N-J1')
response = res.json()

average_mt(response)



