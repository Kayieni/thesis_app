import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from obspy import read_events
from obspy.clients.fdsn import Client
from obspy.imaging.beachball import beach
import os
import numpy as np
import pandas as pd


count2023=0
listofMT = []

def beachball(fm):
    print(fm)
    """
    Plotting the focal mechanism
    """
    filepath=os.path.join("./static/beachballs", ('beachball.png'))
    facecolorb = "b"
    facecolorg = "g"
    facecolory = "yellow"
    facecoloro = "orange"
    facecolorr = "r"

    # radius of the ball
    radius = 100

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)

    # Moment Tensor
    try:
        nofill=True
        focal1 = beach([fm.moment_tensor.tensor.m_rr,fm.moment_tensor.tensor.m_tt,\
        fm.moment_tensor.tensor.m_pp,fm.moment_tensor.tensor.m_rt,\
        fm.moment_tensor.tensor.m_rp,fm.moment_tensor.tensor.m_tp], xy=(0.0,0.0), \
        width=2*radius,axes=None,alpha=1, facecolor=facecolorb, zorder=1)

        ax.add_collection(focal1)

    except:
        # fall back to dc only with color
        nofill=False
    # Planes
    focal2 = beach([fm.nodal_planes.nodal_plane_1.strike,\
    fm.nodal_planes.nodal_plane_1.dip,fm.nodal_planes.nodal_plane_1.rake], \
    nofill=nofill, facecolor=facecolorr, xy=(0.0,0.0),axes=None,width=2*radius,zorder=2)

    ax.add_collection(focal2)

    ax.autoscale_view(tight=False, scalex=True, scaley=True)
    
    # plot the axis
    ax.axison=False
    plt.axis('scaled')
    ax.set_aspect(1)

    fig.savefig(filepath, transparent=True)
    plt.show()


# # calculate the average mt of the area
# def MesosMT():
#     print("")


# event = read_events(
#     'http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?starttime=2023-09-01T00%3A00%3A00&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404', format='QUAKEML')
# print(event)
prev_time = 0
for event in read_events(
    'http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?starttime=2023-01-01T00%3A00%3A00&endtime=2023-02-01T00%3A00%3A00&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404', format='QUAKEML'):
    
    if(event.focal_mechanisms):
        origin = event.preferred_origin() or event.origins[0]
        if(str(origin.time).rsplit(":",1)[0]  == str(prev_time).rsplit(":",1)[0] ):
            continue
        else:
           
            print("---------\nEvent id: " + str(event.resource_id).split('/')[-1] + "\nTime: " +  str(origin.time) )
            if (event.preferred_focal_mechanism_id):
                focmec = list(filter(lambda x: x.resource_id == event.preferred_focal_mechanism_id,event.focal_mechanisms))[0]
            else:
                focmec = event.focal_mechanisms[0]
                
            # print (focmec)
            tensor = focmec.moment_tensor.tensor
            # print(tensor)
            moment_list = [tensor.m_rr, tensor.m_tt, tensor.m_pp,
                        tensor.m_rt, tensor.m_rp, tensor.m_tp]
            print(focmec.nodal_planes.nodal_plane_1.strike,focmec.nodal_planes.nodal_plane_1.dip,focmec.nodal_planes.nodal_plane_1.rake)
            # if count2023 in listofMT:
            listofMT.append(moment_list)
            # else:
            #     listofMT[count2023] = moment_list
            count2023+=1
            # beachball(focmec)
            prev_time = origin.time
    else:
        print("======================================\nEvent doesnt have Focal Mechanisms\nEvent id: " + str(event.resource_id).split('/')[-1] + "\nTime: " + str(origin.time)+"\n========================================")
        continue

df = pd.DataFrame(listofMT)
# print(df)
df.mean()
mesosmt = list(df.mean())
radius = 100
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
nofill=True
focal1 = beach(mesosmt, xy=(0.0,0.0), \
width=2*radius,axes=None,alpha=1, facecolor='r', zorder=1)
ax.add_collection(focal1)
ax.autoscale_view(tight=False, scalex=True, scaley=True)
# plot the axis
ax.axison=False
plt.axis('scaled')
ax.set_aspect(1)

# fig.savefig(filepath, transparent=True)
plt.show()


# output
# 0   -4.658232e+15
# 1   -9.355696e+15
# 2    1.401393e+16
# 3    2.827252e+15
# 4    7.618132e+14
# 5    1.141436e+16
# dtype: float64


# d = {}

# for elem in listofMT:
#     for i in range(len(elem)):
#         if i in d:
#             d[i].append(elem[i])
#         else:
#             d[i] = [elem[i]]

# for k,v in d.items():
#     print(f'The average of idx {k} is {sum(v) / len(v)}')

# output:
# The average of idx 0 is -4658231915789474.0
# The average of idx 1 is -9355695978947368.0
# The average of idx 2 is 1.40139279e+16
# The average of idx 3 is 2827252257894737.0
# The average of idx 4 is 761813231578947.4
# The average of idx 5 is 1.1414359431578948e+16

print(count2023)