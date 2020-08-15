import os
import argparse
from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from siphon.catalog import TDSCatalog
from matplotlib.colors import ListedColormap
import numpy as np

import Map_Utils as map_utils
Utils = map_utils.Utils()


def main():
    # Parse the arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    parser.add_argument('-t', '--time', nargs='+', help='Access and plot weather data X hours from now.', type=int,
                        default=0)
    args = parser.parse_args()

    if args.map == 'verywide':
        map_ = map_utils.VeryWide()
    elif args.map == 'regional':
        map_ = map_utils.Regional()
    elif args.map == 'local':
        map_ = map_utils.Local()
    elif args.map == 'tropical':
        map_ = map_utils.Tropical()
    else:
        print("Invalid Map Type Requested.")
        return

    for t in args.time:
        # Acquire the datasets from the GFS Global Catalog
        GFS_data = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                              'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')

        # Pull out our dataset and get the NCSS access point used to query data from the dataset
        dataset = GFS_data.datasets[0]
        ncss = dataset.subset()

        # Use the `ncss` object to create a new query object
        query = ncss.query()
        time = (datetime.utcnow() + timedelta(hours=t))  # Time of data requested
        query.time(time)
        query.accept('netcdf4')
        query.variables('Precipitation_rate_surface')

        # Set the lat lon box for which specific area of the dataset to query
        if map_.map_type is not 'tropical':
            query.lonlat_box(north=map_.NorthSouthEastWest[0], south=map_.NorthSouthEastWest[1],
                            east=map_.NorthSouthEastWest[2], west=map_.NorthSouthEastWest[3])
        else:
            query.lonlat_box(north=map_.NorthSouthEastWest[0] + 10, south=map_.NorthSouthEastWest[1],
                             east=map_.NorthSouthEastWest[2], west=map_.NorthSouthEastWest[3])

        data = ncss.get_data(query)

        # Grab the keys from the data we want
        precipitations = data.variables['Precipitation_rate_surface']
        latitudes = data.variables['lat']
        longitudes = data.variables['lon']

        # Remove 1d arrays from data for plotting
        precipitations = precipitations[:].squeeze()
        latitudes = latitudes[:].squeeze()
        longitudes = longitudes[:].squeeze()

        # Convert all precipitation values from kg/m^2/s (kilograms per meter squared per second) to inches
        for i in range(len(latitudes)):
            for k in range(len(longitudes)):
                precipitations[i][k] = kg_per_msquared_to_inches(precipitations[i][k])

        # Combine 1D latitude and longitudes into a 2D grid of locations
        lon_2d, lat_2d = np.meshgrid(longitudes, latitudes)

        # Create figure for plotting
        fig = plt.figure(figsize=(15, 9))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(map_.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())

        # Add map features depending on map type
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
        if map_.map_type == 'regional' or map_.map_type == 'local':
            reader = shpreader.Reader('../county_data/countyl010g.shp')
            counties = list(reader.geometries())
            COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
            ax.add_feature(COUNTIES, facecolor='none', edgecolor='black', linewidth=0.3)
        elif map_.map_type == 'tropical':
            countries = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_0_countries',
                scale='50m',
                facecolor='none')
            ax.add_feature(cfeature.LAND)
            ax.add_feature(countries, edgecolor='black', linewidth=0.5)

        # Create the custom color map for rain
        colormap = ListedColormap(['white',
                                   # Greens
                                   '#7dcf65', '#6fba59', '#63a351',
                                   '#5c914d', '#508641', '#48793b',
                                   '#396a2d', '#315d27', '#245817',
                                   '#1c4711', '#1c4711', '#1c4711',
                                   '#1c4711', '#1c4711', '#1c4711',
                                   # Oranges
                                   '#ffea5d', '#ffea5d', '#dddf32', '#dfcc4b', '#DBC634', 'orange'])

        # Contour temperature at each lat/long
        cf = ax.contourf(lon_2d, lat_2d, precipitations,
                         levels=[0.001, 0.01, 0.025, 0.045, 0.065, 0.085, 0.105, 0.125, 0.150,
                                 0.175, 0.200, 0.250, 0.5, 1.0],
                         extend='both',
                         transform=ccrs.PlateCarree(),
                         cmap=colormap)

        # Plot a colorbar to show temperature and reduce the size of it
        colorbar = plt.colorbar(cf, ax=ax, cmap=colormap, fraction=0.032,
                     ticks=[0.001, 0.01, 0.025, 0.045, 0.065, 0.085, 0.105, 0.125, 0.150, 0.175, 0.200,
                            0.250, 0.500, 1.00])
        colorbar.set_label('Precipitation Rate (inches per hour)')

        # Plot all the cities
        if map_.map_type is not 'tropical':
            for city in map_.cities:
                ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
                cityName_latlon = Utils.plot_latlon_cityName_by_maptype(lat=city.lat, lon=city.lon, map_type=map_.map_type)
                ax.text(cityName_latlon[1], cityName_latlon[0], city.city_name, fontsize='small', fontweight='bold',
                        transform=ccrs.PlateCarree())

        # Create a title with the time value
        ax.set_title('Precipitation Rate Forecast (inches) for {} UTC'.format(str(time)[:-7]),
                     fontsize=12, loc='left')

        # Company copyright
        text = AnchoredText(r'$\mathcircled{{c}}$ NickelBlock Forecasting',
                            loc=4, prop={'size': 9}, frameon=True)
        ax.add_artist(text)

        # Data model
        data_model = AnchoredText('GFS 12z model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)

        # Add logo
        logo = Utils.get_logo()
        if map_.map_type is not 'tropical':
            ax.figure.figimage(logo, 1105, 137, zorder=1)
        else:
            ax.figure.figimage(logo, 1105, 181, zorder=1)

        plt.savefig('{}_Precipitation_Hour_{}.png'.format(map_.map_type, t))


def kg_per_msquared_to_inches(num):
    result = (num * 86400) * 0.03937008
    return result


if __name__ == '__main__':
    Utils.create_output_directory()
    main()
