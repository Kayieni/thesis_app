import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from obspy import read_events
from obspy.clients.fdsn import Client
from obspy.imaging.beachball import beach
import os
import numpy as np

event = read_events(
    'http://orfeus.gein.noa.gr:8085/fdsnws/event/1/query?starttime=2023-09-04T00%3A00%3A00&includefocalmechanism=true&includeallfocalmechanisms=true&nodata=404', format='QUAKEML')[1]
print(event)
origin = event.preferred_origin() or event.origins[0]
focmec = event.preferred_focal_mechanism() or event.focal_mechanisms[0]
tensor = focmec.moment_tensor.tensor
# print(tensor)
moment_list = [tensor.m_rr, tensor.m_tt, tensor.m_pp,
               tensor.m_rt, tensor.m_rp, tensor.m_tp]

# projection = ccrs.PlateCarree(central_longitude=0.0)
# print(projection)
# x, y = projection.transform_point(x=origin.longitude, y=origin.latitude,
#                                   src_crs=ccrs.Geodetic())

# fig = plt.figure(dpi=150)
# ax = fig.add_subplot(111, projection=projection)
# ax.set_extent((-180, 180, -90, 90))
# ax.coastlines()
# ax.gridlines()

# b = beach(moment_list, xy=(x, y), width=20, linewidth=1, alpha=1, zorder=10)
# b.set_zorder(10)
# ax.add_collection(b)
# fig.show()
# plt.show()


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
        width=2*radius,axes=None,alpha=1, facecolor=facecoloro, zorder=1)

        ax.add_collection(focal1)

    except:
        # fall back to dc only with color
        nofill=False
    # Planes
    focal2 = beach([fm.nodal_planes.nodal_plane_1.strike,\
    fm.nodal_planes.nodal_plane_1.dip,fm.nodal_planes.nodal_plane_1.rake], \
    nofill=nofill, facecolor=facecoloro, xy=(0.0,0.0),axes=None,width=2*radius,zorder=2)

    ax.add_collection(focal2)

    ax.autoscale_view(tight=False, scalex=True, scaley=True)
    
    # plot the axis
    ax.axison=False
    plt.axis('scaled')
    ax.set_aspect(1)

    fig.savefig(filepath, transparent=True)
    plt.show()




beachball(focmec)