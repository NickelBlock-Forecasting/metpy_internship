from datetime import datetime, timedelta
import argparse

from netCDF4 import num2date
from siphon.catalog import TDSCatalog

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import numpy as np


class City:
    def __init__(self, city_name, lat, lon, temp=None):
        self.city_name = city_name
        self.lat = lat
        self.lon = lon
        self.temp = temp


def round_temps(x):
    return round(x * 4) / 4


def main():
    # Parse the arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', help='Access and plot weather data X hours from now.', type=int,
                        default=0)
    args = parser.parse_args()

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
    time = (datetime.utcnow() + timedelta(hours=args.time))  # Time of data requested
    query.time(time)
    query.accept('netcdf4')
    query.variables('Temperature_surface')

    # We construct a query asking for data corresponding to a latitude and longitude box where 43
    # lat is the northern extent, 35 lat is the southern extent, -111 long is the western extent
    # and -100 is the eastern extent. We request the data for the current time.
    #
    # We also ask for NetCDF version 4 data, for the variable 'temperature_surface'. This request
    # will return all surface temperatures for points in our bounding box for a single time,
    # nearest to that requested. Note the string representation of the query is a properly encoded
    # query string.
    # Translate Set Extent --> -97.5, -15.5, 8.5, 30.5
    query.lonlat_box(north=40.5, south=8.5, east=-15.5, west=-97.5)

    # We now request data from the server using this query. The `NCSS` class handles parsing
    # this NetCDF data (using the `netCDF4` module). If we print out the variable names, we see
    # our requested variable, as well as the coordinate variables (needed to properly reference
    # the data).
    data = ncss.get_data(query)

    # We'll pull out the useful variables for temperature, latitude, and longitude, and time
    # (which is the time, in hours since the forecast run).
    temp_var = data.variables['Temperature_surface']

    # Time variables can be renamed in GRIB collections. Best to just pull it out of the
    # coordinates attribute on temperature
    time_name = temp_var.coordinates.split()[1]
    time_var = data.variables[time_name]
    lat_var = data.variables['lat']
    lon_var = data.variables['lon']

    # Now we make our data suitable for plotting.
    # Get the actual data values and remove any size 1 dimensions
    temp_vals = temp_var[:].squeeze()
    lat_vals = lat_var[:].squeeze()
    lon_vals = lon_var[:].squeeze()

    # Convert temps to Fahrenheit from Kelvin
    temp_vals = temp_vals * 1.8 - 459.67

    # Combine 1D latitude and longitudes into a 2D grid of locations
    lon_2d, lat_2d = np.meshgrid(lon_vals, lat_vals)

    # Now we can plot these up using matplotlib and cartopy.
    # Create the figure and set the frame
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-97.5, -15.5, 8.5, 30.5], crs=ccrs.Geodetic())

    # Create all desired boundaries
    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    countries = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='50m',
        facecolor='none')
    ax.add_feature(cfeature.LAND)
    ax.add_feature(countries, edgecolor='black', linewidth=0.5)

    # Contour temperature at each lat/long
    cf = ax.contourf(lon_2d, lat_2d, temp_vals, 50, extend='both', transform=ccrs.PlateCarree(),
                     cmap='coolwarm')

    # Plot a colorbar to show temperature and reduce the size of it
    plt.colorbar(cf, ax=ax, fraction=0.032)

    # Make a title with the time value
    ax.set_title('Temperature forecast (\u00b0F) for ' + str(time) + ' UTC',
                 fontsize=12, loc='left')

    # Company copyright on the bottom right corner
    SOURCE = 'NickelBlock Forecasting'
    text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                        ''.format(SOURCE),
                        loc=4, prop={'size': 9}, frameon=True)
    ax.add_artist(text)
    plt.show()


if __name__ == '__main__':
    main()
