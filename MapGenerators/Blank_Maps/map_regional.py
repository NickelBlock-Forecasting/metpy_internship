import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.image as mat_img
import matplotlib.figure
import matplotlib.image as mpimg
from matplotlib.offsetbox import AnchoredText, OffsetImage,  AnnotationBbox
import numpy as np
from PIL import Image


class City:
    def __init__(self, city_name, lat, lon):
        self.city_name = city_name
        self.lat = lat
        self.lon = lon


def main():

    reader = shpreader.Reader('./county_data/countyl010g.shp')
    counties = list(reader.geometries())
    COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

    ### List out all the cities you want plotted
    #  - MISSISSIPPI
    hattiesburg = City('Hattiesburg', 31.3271, -89.2903)
    jackson = City('Jackson', 32.2988, -90.1848)
    tupelo = City('Tupelo', 34.2576, -88.7034)
    # - LOUISIANA
    new_orleans = City('New Orleans', 29.9511, -90.0715)
    baton_rouge = City('Baton Rouge', 30.4515, -91.1871)
    shreveport = City('Shreveport', 32.5252, -93.7502)
    # - ALABAMA
    mobile = City('Mobile', 30.6954, -88.0399)
    montgomery = City('Montgomery', 32.3792, -86.3077)
    tuscaloosa = City('Tuscaloosa', 33.2098, -87.5692)
    huntsville = City('Huntsville', 34.7304, -86.5861)
    dothan = City('Dothan', 31.2232, -85.3905)
    # - TENNESSEE
    memphis = City('Memphis', 35.1495, -90.0490)
    jackson_tenn = City('Jackson', 35.6145, -88.8139)
    clarksville = City('Clarksville', 36.5298, -87.3595)
    knoxville = City('Knoxville', 35.9606, -83.9207)
    # - GEORGIA
    atlanta = City('Atlanta', 33.7490, -84.3880)
    macon = City('Macon', 32.8407, -83.6324)
    # - FLORIDA
    pensacola = City('Pensacola', 30.4213, -87.2169)
    tallahassee = City('Tallahassee', 30.4383, -84.2807)
    jacksonville = City('Jacksonville', 30.3322, -81.6557)
    # - ARKANSAS
    little_rock = City('Little Rock', 34.7465, -92.2896)
    fort_smith = City('Fort Smith', 35.3859, -94.3985)
    # - SOUTH CAROLINA
    augusta = City('Augusta', 33.4735, -82.0105)
    # - TEXAS
    houston = City('Houston', 29.7604, -95.3698)
    ###

    cities = [
        hattiesburg,
        jackson,
        tupelo,

        new_orleans,
        baton_rouge,

        mobile,
        montgomery,
        tuscaloosa,
        huntsville,
        dothan,

        memphis,

        pensacola,

        little_rock,
    ]

    # Create the figure and set the frame
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-93.5, -84.5, 28.5, 35.5], crs=ccrs.Geodetic())

    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')

    # Features for the figure
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE, edgecolor='lightgray')
    ax.add_feature(COUNTIES, facecolor='none', edgecolor='lightgray')
    ax.add_feature(states_provinces, edgecolor='gray')

    # Plot all the cities
    for city in cities:
        ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.5, transform=ccrs.Geodetic())
        ax.text(city.lon, city.lat, city.city_name, fontsize='x-small',
                transform=ccrs.PlateCarree())

    # Company copyright on the bottom right corner
    SOURCE = 'NickelBlock Forecasting'
    text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                        ''.format(SOURCE),
                        loc=4, prop={'size': 9}, frameon=True)
    ax.add_artist(text)

    plt.show()


if __name__ == '__main__':
    main()
