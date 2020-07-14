from datetime import datetime, timedelta
import argparse
import os

from siphon.catalog import TDSCatalog

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.colors import ListedColormap
import numpy as np

import Map_Info as map_info


def round_temps(x):
    return round(x * 4) / 4


def main():
    # Parse the arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    parser.add_argument('-t', '--time', nargs='+', help='Access and plot weather data X hours from now.', type=int,
                        default=0)
    args = parser.parse_args()

    if args.map == 'verywide':
        temp_map = map_info.VeryWide()
    elif args.map == 'regional':
        temp_map = map_info.Regional()
    elif args.map == 'local':
        temp_map = map_info.Local()
    elif args.map == 'tropical':
        temp_map = map_info.Tropical()

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
        query.variables('Temperature_surface')

        # We construct a query asking for data corresponding to a latitude and longitude box where 43
        # lat is the northern extent, 35 lat is the southern extent, -111 long is the western extent
        # and -100 is the eastern extent. We request the data for the current time.
        #
        # We also ask for NetCDF version 4 data, for the variable 'temperature_surface'. This request
        # will return all surface temperatures for points in our bounding box for a single time,
        # nearest to that requested. Note the string representation of the query is a properly encoded
        # query string.
        #
        # Translate Set Extent
        if temp_map.map_type is not 'tropical':
            query.lonlat_box(north=temp_map.NorthSouthEastWest[0], south=temp_map.NorthSouthEastWest[1],
                            east=temp_map.NorthSouthEastWest[2], west=temp_map.NorthSouthEastWest[3])
        else:
            query.lonlat_box(north=temp_map.NorthSouthEastWest[0] + 10, south=temp_map.NorthSouthEastWest[1],
                             east=temp_map.NorthSouthEastWest[2], west=temp_map.NorthSouthEastWest[3])

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
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(temp_map.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())

        # Add state boundaries to plot
        if temp_map.map_type == 'verywide':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
        elif temp_map.map_type == 'regional' or temp_map.map_type == 'local':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
            reader = shpreader.Reader('../county_data/countyl010g.shp')
            counties = list(reader.geometries())
            COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
            ax.add_feature(COUNTIES, facecolor='none', edgecolor='black', linewidth=0.3)
        elif temp_map.map_type == 'tropical':
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

        # Plot all the cities
        if temp_map.map_type is not 'tropical':
            for city in temp_map.cities:
                for lat in range(len(lat_vals)):
                    for lon in range(len(lon_vals)):
                        if round_temps(city.lat) == lat_vals[lat] and round_temps(city.lon) == (lon_vals[lon] - 360):
                            ax.text(city.lon + 0.09, city.lat - 0.2, int(round(temp_vals[lat][lon])), fontsize='10',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
                ax.text(city.lon - 0.5, city.lat + 0.09, city.city_name, fontsize='small', fontweight='bold',
                        transform=ccrs.PlateCarree())

        # Make a title with the time value
        time = str(time)[:-7]
        ax.set_title('Temperature forecast (\u00b0F) for ' + time + ' UTC',
                     fontsize=12, loc='left')

        # Company copyright on the bottom right corner
        SOURCE = 'NickelBlock Forecasting'
        text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                            ''.format(SOURCE),
                            loc=4, prop={'size': 9}, frameon=True)
        data_model = AnchoredText('GFS 12z model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)
        ax.add_artist(text)

        plt.savefig('{}_Temperature_Hour_{}.png'.format(temp_map.map_type, t))


def make_output_directory():
    if not os.path.exists('output'):
        os.mkdir('output')
    os.chdir('output')


if __name__ == '__main__':
    make_output_directory()
    main()
