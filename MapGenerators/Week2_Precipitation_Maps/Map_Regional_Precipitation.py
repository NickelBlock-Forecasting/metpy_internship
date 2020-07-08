from datetime import datetime, timedelta
import argparse
import os
import shutil

from netCDF4 import num2date
from siphon.catalog import TDSCatalog

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import numpy as np


class City:
    def __init__(self, city_name, lat, lon, temp=None):
        self.city_name = city_name
        self.lat = lat
        self.lon = lon
        self.temp = temp


def kg_per_msquared_to_inches(num):
    result = ((num * 86400) / 24) * 0.0393701
    if result >= 0.5:
        result = 0.5
    return result


def main():
    # Parse the arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', nargs='+', help='Access and plot weather data X hours from now.', type=int,
                        default=0)
    args = parser.parse_args()

    # List out all the cities you want plotted
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

    for t in args.time:
        # Next,  we construct a `TDSCatalog` instance pointing to our dataset of interest, in
        # this case TDS' "Best" virtual dataset for the GFS global 0.25 degree collection of
        # GRIB files. This will give us a good resolution for our map. This catalog contains a
        # single dataset.
        best_gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                              'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')

        # We pull out this dataset and get the NCSS access point
        best_ds = best_gfs.datasets[0]
        ncss = best_ds.subset()

        # We can then use the `ncss` object to create a new query object, which
        # facilitates asking for data from the server.
        query = ncss.query()
        time = (datetime.utcnow() + timedelta(hours=t))  # Time of data requested
        query.time(time)
        query.accept('netcdf4')
        query.variables('Precipitation_rate_surface')

        # We construct a query asking for data corresponding to a latitude and longitude box where 43
        # lat is the northern extent, 35 lat is the southern extent, -111 long is the western extent
        # and -100 is the eastern extent. We request the data for the current time.
        #
        # We also ask for NetCDF version 4 data, for the variable 'temperature_surface'. This request
        # will return all surface temperatures for points in our bounding box for a single time,
        # nearest to that requested. Note the string representation of the query is a properly encoded
        # query string.
        # Translate Set Extent --> -93.5, -84.5, 28.5, 35.5
        query.lonlat_box(north=35.5, south=28.5, east=-84.5, west=-93.5)

        # We now request data from the server using this query. The `NCSS` class handles parsing
        # this NetCDF data (using the `netCDF4` module). If we print out the variable names, we see
        # our requested variable, as well as the coordinate variables (needed to properly reference
        # the data).
        data = ncss.get_data(query)

        # We'll pull out the useful variables for temperature, latitude, and longitude, and time
        # (which is the time, in hours since the forecast run).
        precipitation_var = data.variables['Precipitation_rate_surface']

        # Time variables can be renamed in GRIB collections. Best to just pull it out of the
        # coordinates attribute on temperature
        time_name = precipitation_var.coordinates.split()[1]
        time_var = data.variables[time_name]
        lat_var = data.variables['lat']
        lon_var = data.variables['lon']

        # Now we make our data suitable for plotting.
        # Get the actual data values and remove any size 1 dimensions
        precipitation_vals = precipitation_var[:].squeeze()
        lat_vals = lat_var[:].squeeze()
        lon_vals = lon_var[:].squeeze()

        # Convert all precipitation values from kg/m^2/s (kilograms per meter squared per second) to inches
        for i in range(len(lat_vals)):
            for k in range(len(lon_vals)):
                precipitation_vals[i][k] = kg_per_msquared_to_inches(precipitation_vals[i][k])

        # Combine 1D latitude and longitudes into a 2D grid of locations
        lon_2d, lat_2d = np.meshgrid(lon_vals, lat_vals)

        # Now we can plot these up using matplotlib and cartopy.
        # Create the figure and set the frame
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent([-93.5, -84.5, 28.5, 35.5], crs=ccrs.Geodetic())

        # Create all desired boundaries
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
        reader = shpreader.Reader('./county_data/countyl010g.shp')
        counties = list(reader.geometries())
        COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
        ax.add_feature(COUNTIES, facecolor='none', edgecolor='black', linewidth=0.3)

        # Create the custom color map for rain
        colormap = ListedColormap(['white',
                                   # Greens
                                   '#e0f7d8', '#ccf7be', '#b8f4a4', '#9AD58A', '#a1d691', '#9ac48e', '#86bc77', '#72ab62',
                                   '#659f55', '#81C16F', '#5c914d', '#508641', '#48793b', '#396a2d', '#315d27', '#245817',
                                   '#1c4711',
                                   'yellow',
                                   # Oranges
                                   '#ffea5d', '#dddf32', '#dfcc4b', '#DBC634', 'orange'])

        # Contour temperature at each lat/long
        cf = ax.contourf(lon_2d, lat_2d, precipitation_vals,
                         levels=[0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.125, 0.150, 0.175, 0.2, 0.225, 0.250, 0.275
                             , 0.3, 0.325, 0.350, 0.375, 0.4, 0.425, 0.450, 0.475, 0.5], extend='both',
                         transform=ccrs.PlateCarree(),
                         cmap=colormap)

        # Plot a colorbar to show temperature and reduce the size of it
        plt.colorbar(cf, ax=ax, cmap=colormap, fraction=0.032,
                     ticks=[0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])

        # Plot all the cities
        for city in cities:
            ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
            ax.text(city.lon - 0.3, city.lat + 0.06, city.city_name, fontsize='small', fontweight='bold',
                    transform=ccrs.PlateCarree())

        # Make a title with the time value
        time = str(time)[:-7]
        ax.set_title('Precipitation Rate Forecast (inches) for ' + time + ' UTC',
                     fontsize=12, loc='left')

        # Company copyright on the bottom right corner
        SOURCE = 'NickelBlock Forecasting'
        text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                            ''.format(SOURCE),
                            loc=4, prop={'size': 9}, frameon=True)
        data_model = AnchoredText('GFS 12z model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)
        ax.add_artist(text)

        plt.savefig('Regional_Precipitation_Hour_{}.png'.format(t))
        shutil.move(os.getcwd() + '/Regional_Precipitation_Hour_{}.png'.format(t),
                    os.getcwd() + '/output/Regional_Precipitation_Hour_{}.png'.format(t))


def make_output_directory():
    if not os.path.exists('output'):
        os.mkdir('output')


if __name__ == '__main__':
    make_output_directory()
    main()
