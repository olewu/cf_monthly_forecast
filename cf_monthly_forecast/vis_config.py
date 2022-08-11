# Define some plot specific configurations:

from mpl_toolkits.basemap import Basemap

area_specs = {
    'EUROPE': dict(
        lon0 = -20,
        lon1 = 50,
        lat0 = 35,
        lat1 = 72,
        bm = Basemap(
            resolution = 'l', 
            projection = 'gall',
            llcrnrlon = -20.,
            llcrnrlat = 35.,
            urcrnrlon = 50.,
            urcrnrlat = 72.,
            fix_aspect = False
        ),
        aspectratio = 1.5
    ),
    'GLOBAL': dict(
        lon0 = -180,
        lon1 = 180,
        lat0 = -90,
        lat1 = 90,
        bm = Basemap(projection='moll',lon_0=0,resolution='c'),
        aspectratio = 2.05
    )
}



    # 'EUROPE_SMALL': dict(
    #     lon0 = 0,
    #     lon1 = 30,
    #     lat0 = 54,
    #     lat1 = 71.5,
    #     bm = Basemap(
    #         resolution = 'i', 
    #         projection = 'gall',
    #         llcrnrlon = 0,
    #         llcrnrlat = 54,
    #         urcrnrlon = 30,
    #         urcrnrlat = 71.5,
    #         fix_aspect = False
    #     ),
    #     aspectratio = 1.1
    # ),