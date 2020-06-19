import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.image as mat_img
import matplotlib.figure
import cartopy.feature as cfeature
from matplotlib.offsetbox import AnchoredText, OffsetImage,  AnnotationBbox
import matplotlib.image as mpimg
from PIL import Image
import numpy as np
import pygrib

class Country:
    def __init__(self, country_name, lat, lon):
        self.country_name = country_name
        self.lat = lat
        self.lon = lon


def main():

    # Create the figure and set the frame
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-97.5, -15.5, 8.5, 30.5], crs=ccrs.Geodetic())

    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    countries = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='50m',
        facecolor='none')

    # Features for the figure
    ax.add_feature(cfeature.LAND)
    ax.add_feature(countries, edgecolor='lightgray')
    ax.add_feature(cfeature.COASTLINE, edgecolor='lightgray')

    # Plot all the cities
    # for city in cities:
    #     ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.5, transform=ccrs.Geodetic())
    #     ax.text(city.lon, city.lat, city.city_name, fontsize='x-small',
    #             transform=ccrs.PlateCarree())

    # Company copyright on the bottom right corner
    SOURCE = 'NickelBlock Forecasting'
    text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                        ''.format(SOURCE),
                        loc=4, prop={'size': 9}, frameon=True)
    ax.add_artist(text)

    plt.show()


if __name__ == '__main__':
    main()
