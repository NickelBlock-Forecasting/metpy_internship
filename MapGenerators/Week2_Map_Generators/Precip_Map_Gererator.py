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


def kg_per_msquared_to_inches(num):
    result = (num * 86400) * 0.03937008
    return result


def main():
    # Parse the arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    parser.add_argument('-t', '--time', nargs='+', help='Access and plot weather data X hours from now.', type=int,
                        default=0)
    args = parser.parse_args()

    if args.map == 'verywide':
        precip_map = map_info.VeryWide()
    elif args.map == 'regional':
        precip_map = map_info.Regional()
    elif args.map == 'local':
        precip_map = map_info.Local()
    elif args.map == 'tropical':
        precip_map = map_info.Tropical()

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
        #
        # Translate Set Extent
        if precip_map.map_type is not 'tropical':
            query.lonlat_box(north=precip_map.NorthSouthEastWest[0], south=precip_map.NorthSouthEastWest[1],
                            east=precip_map.NorthSouthEastWest[2], west=precip_map.NorthSouthEastWest[3])
        else:
            query.lonlat_box(north=precip_map.NorthSouthEastWest[0] + 10, south=precip_map.NorthSouthEastWest[1],
                             east=precip_map.NorthSouthEastWest[2], west=precip_map.NorthSouthEastWest[3])

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
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(precip_map.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())

        # Add state boundaries to plot
        if precip_map.map_type == 'verywide':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
        elif precip_map.map_type == 'regional' or precip_map.map_type == 'local':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
            reader = shpreader.Reader('../county_data/countyl010g.shp')
            counties = list(reader.geometries())
            COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
            ax.add_feature(COUNTIES, facecolor='none', edgecolor='black', linewidth=0.3)
        elif precip_map.map_type == 'tropical':
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
        cf = ax.contourf(lon_2d, lat_2d, precipitation_vals,
                         levels=[0.001, 0.01, 0.025, 0.045, 0.065, 0.085, 0.105, 0.125, 0.150,
                                 0.175, 0.200, 0.250, 0.5, 1.0],
                         extend='both',
                         transform=ccrs.PlateCarree(),
                         cmap=colormap)

        # Plot a colorbar to show temperature and reduce the size of it
        plt.colorbar(cf, ax=ax, cmap=colormap, fraction=0.032,
                     ticks=[0.001, 0.01, 0.025, 0.045, 0.065, 0.085, 0.105, 0.125, 0.150, 0.175, 0.200,
                            0.250, 0.500, 1.00])

        # Plot all the cities
        if precip_map.map_type is not 'tropical':
            for city in precip_map.cities:
                ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
                ax.text(city.lon - 0.5, city.lat + 0.09, city.city_name, fontsize='small', fontweight='bold',
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

        plt.savefig('{}_Precipitation_Hour_{}.png'.format(precip_map.map_type, t))


def make_output_directory():
    if not os.path.exists('output'):
        os.mkdir('output')
    os.chdir('output')


if __name__ == '__main__':
    make_output_directory()
    main()
