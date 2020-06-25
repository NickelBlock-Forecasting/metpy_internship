# Copyright (c) 2013-2015 Siphon Contributors.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""
================
NCSS and CartoPy
================

Use Siphon to query the NetCDF Subset Service (NCSS) and plot on a map.

This example uses Siphon's NCSS class to provide temperature data
for contouring a basic map using CartoPy.
"""
from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pytz
from matplotlib.offsetbox import AnchoredText
from netCDF4 import num2date
from siphon.catalog import TDSCatalog


class City:
    def __init__(self, city_name, lat, lon, temp=None):
        self.city_name = city_name
        self.lat = lat
        self.lon = lon
        self.temp = temp


def round_temps(x):
    return round(x * 4) / 4

###########################################
# List out all the cities you want plotted
#  - MISSISSIPPI
hattiesburg = City('Hattiesburg', 31.3271, -89.2903)
jackson = City('Jackson', 32.2988, -90.1848)
tupelo = City('Tupelo', 34.2576, -88.7034)
# -LOUISIANA
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
    shreveport,

    mobile,
    montgomery,
    tuscaloosa,
    huntsville,
    dothan,

    memphis,
    jackson_tenn,
    clarksville,
    knoxville,

    atlanta,
    macon,

    pensacola,
    tallahassee,
    jacksonville,

    little_rock,
    fort_smith,

    augusta,

    houston
]

###########################################
# Next,  we construct a `TDSCatalog` instance pointing to our dataset of interest, in
# this case TDS' "Best" virtual dataset for the GFS global 0.25 degree collection of
# GRIB files. This will give us a good resolution for our map. This catalog contains a
# single dataset.

best_gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                      'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')

###########################################
# We pull out this dataset and get the NCSS access point
best_ds = best_gfs.datasets[0]
ncss = best_ds.subset()

###########################################
# We can then use the `ncss` object to create a new query object, which
# facilitates asking for data from the server.
query = ncss.query().time(datetime.now(pytz.timezone('America/Chicago'))).accept('netcdf4')
query.variables('Temperature_surface')

###########################################
# We construct a query asking for data corresponding to a latitude and longitude box where 43
# lat is the northern extent, 35 lat is the southern extent, -111 long is the western extent
# and -100 is the eastern extent. We request the data for the current time.
#
# We also ask for NetCDF version 4 data, for the variable 'temperature_surface'. This request
# will return all surface temperatures for points in our bounding box for a single time,
# nearest to that requested. Note the string representation of the query is a properly encoded
# query string.
# -97, -81, 28, 37

query.lonlat_box(north=37, south=28, east=-81, west=-97)

###########################################
# We now request data from the server using this query. The `NCSS` class handles parsing
# this NetCDF data (using the `netCDF4` module). If we print out the variable names, we see
# our requested variable, as well as the coordinate variables (needed to properly reference
# the data).
data = ncss.get_data(query)

###########################################

# We'll pull out the useful variables for temperature, latitude, and longitude, and time
# (which is the time, in hours since the forecast run).
temp_var = data.variables['Temperature_surface']

# Time variables can be renamed in GRIB collections. Best to just pull it out of the
# coordinates attribute on temperature
time_name = temp_var.coordinates.split()[1]
time_var = data.variables[time_name]
lat_var = data.variables['lat']
lon_var = data.variables['lon']

###########################################
# Now we make our data suitable for plotting.
# Get the actual data values and remove any size 1 dimensions

temp_vals = temp_var[:].squeeze()
lat_vals = lat_var[:].squeeze()
lon_vals = lon_var[:].squeeze()

# Convert the number of hours since the reference time to an actual date
time_val = num2date(time_var[:].squeeze(), time_var.units)

# Convert temps to Fahrenheit from Kelvin
temp_vals = temp_vals * 1.8 - 459.67

# for lat in range(len(lat_vals)):
#     for lon in range(len(lon_vals)):
#         print('Latitude: ', lat_vals[lat], '  Longitude: -', 360 - lon_vals[lon], '  Temperature: ', temp_vals[lat][lon])

# Combine 1D latitude and longitudes into a 2D grid of locations
lon_2d, lat_2d = np.meshgrid(lon_vals, lat_vals)

###########################################
# Now we can plot these up using matplotlib and cartopy.
# Create the figure and set the frame
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
ax.set_extent([-97, -81, 28, 37], crs=ccrs.Geodetic())

# Add state boundaries to plot
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)

# Contour temperature at each lat/long
cf = ax.contourf(lon_2d, lat_2d, temp_vals, 200, extend='both', transform=ccrs.PlateCarree(),
                 cmap='coolwarm')

# Plot a colorbar to show temperature and reduce the size of it
plt.colorbar(cf, ax=ax, fraction=0.032)

# Plot all the cities
for city in cities:
    for lat in range(len(lat_vals)):
        for lon in range(len(lon_vals)):
            if round(city.lat) == lat_vals[lat] and round(city.lon) == -abs(360 - lon_vals[lon]):
                # print(city.city_name, ': Lat ', round(city.lat), '  Lon: ', round(city.lon))
                # print('Shown : Lat ', lat_vals[lat], '  Lon: ', -abs(360 - lon_vals[lon]))
                ax.text(city.lon, city.lat - 0.02, temp_vals[lat][lon], fontsize='small', transform=ccrs.PlateCarree())
    ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.75, transform=ccrs.Geodetic())
    ax.text(city.lon - 0.5, city.lat + 0.09, city.city_name, fontsize='small', fontweight='bold',
            transform=ccrs.PlateCarree())

# Company copyright on the bottom right corner
SOURCE = 'NickelBlock Forecasting'
text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                    ''.format(SOURCE),
                    loc=4, prop={'size': 9}, frameon=True)
ax.add_artist(text)
plt.show()
