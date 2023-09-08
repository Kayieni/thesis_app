from obspy.imaging.beachball import beachball, beach
from obspy.core.event.event import Event
from obspy.core.event.origin import Origin
from obspy.core.event.magnitude import Magnitude
from obspy.core.event.catalog import Catalog
from obspy.core.event import read_events
import requests
import matplotlib.pyplot as plt



# try:
#     # connect database
#     db = mysql.connect(
#         host='localhost',
#         user='root',
#         database = 'thesis',
#         passwd='',
#     )

# except Error as e:
#     print("Error while connecting to MySQL. \n", e)

# r = requests.get('http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?'+starttime+'includeallorigins=true&includeallmagnitudes=false&includefocalmechanism=true&nodata=404')
r = requests.get("http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?starttime=2023-09-04T00%3A00%3A00&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404")


with open("obs2.xml",'wb') as f:
    f.write(r.content)

for evt in read_events("obs2.xml"):
    print(evt)
    fm = evt.focal_mechanisms[0]
    print(fm)
    np1 = fm.nodal_planes.nodal_plane_1
    print(np1)
    mt = [np1.strike,np1.dip,np1.rake]
    beachball(mt, size=200, linewidth=2, facecolor='r')

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)
    
    focal2 = beach([fm.nodal_planes.nodal_plane_1.strike,\
        fm.nodal_planes.nodal_plane_1.dip,fm.nodal_planes.nodal_plane_1.rake])
    ax.add_collection(focal2)
    plt.show()
    




