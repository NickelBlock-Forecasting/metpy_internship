import os
import argparse

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import pygrib

import Map_Utils as map_utils
Utils = map_utils.Utils()


def main():
    download_dataset()

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    args = parser.parse_args()

    if args.map == 'verywide':
        map_ = map_utils.VeryWide()
    elif args.map == 'regional':
        map_ = map_utils.Regional()
    elif args.map == 'local':
        map_ = map_utils.Local()
    else:
        print("Invalid Map Type Requested.")
        return

    # Open dataset
    file = '../output/DHLPCoR_data.grb2'
    data = pygrib.open(file)

    # Grab the keys from the data we want
    maximum_temperatures = data.select(name='Maximum temperature')
    minimum_temperatures = data.select(name='Minimum temperature')
    percent_chance_rain = data.select(name='Probability of 0.01 inch of precipitation (POP)')

    # loops Day by day (1-5)
    day = 1
    for max_temperatures, min_temperatures, percent_chance_rains in zip(maximum_temperatures, minimum_temperatures,  percent_chance_rain):
        # Max Temperature data
        max_temperature_data = []
        max_temp_latitudes, max_temp_longitudes = max_temperatures.latlons()
        max_temp_values = max_temperatures.values
        for latitudes, longitudes, values in zip(max_temp_latitudes, max_temp_longitudes, max_temp_values):
            for lat, lon, value in zip(latitudes, longitudes, values):
                max_temperature_data.append({'lat': lat, 'lon': lon, 'value': value})

        # Min Temperature data
        min_temperature_data = []
        min_temp_lats, min_temp_lons = min_temperatures.latlons()
        min_temp_values = min_temperatures.values
        for latitudes, longitudes, values in zip(min_temp_lats, min_temp_lons, min_temp_values):
            for lat, lon, value in zip(latitudes, longitudes, values):
                min_temperature_data.append({'lat': lat, 'lon': lon, 'value': value})

        # Percent chance of rain data
        percent_chance_rain_data = []
        per_chance_rain_lats, per_chance_rain_lons = percent_chance_rains.latlons()
        per_chance_rain_values = percent_chance_rains.values
        for latitudes, longitudes, values in zip(per_chance_rain_lats, per_chance_rain_lons, per_chance_rain_values):
            for lat, lon, value in zip(latitudes, longitudes, values):
                percent_chance_rain_data.append({'lat': lat, 'lon': lon, 'value': value})

        # Create the figure for graphing
        fig = plt.figure(figsize=(15, 9))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(map_.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())

        # Add boundaries to plot
        ax.add_feature(cfeature.OCEAN, facecolor=cfeature.COLORS['water'])
        if map_.map_type == 'verywide':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, facecolor=cfeature.COLORS['land'])
        elif map_.map_type == 'regional' or map_.map_type == 'local':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5, facecolor=cfeature.COLORS['land'])
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

        # Set the additional info on the map
        ax.set_title('Daily High / Low / Percent Chance of Rain taken ' + str(max_temperatures.validDate)[:-9] + ' UTC',
                     fontsize=12, loc='left')
        text = AnchoredText(r'$\mathcircled{{c}}$ NickelBlock Forecasting',
                            loc=4, prop={'size': 9}, frameon=True)
        ax.add_artist(text)

        # Data Model
        data_model = AnchoredText('NWS/NDFD CONUS model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)

        # Add logo
        logo = Utils.get_logo()
        if map_.map_type == 'verywide':
            ax.figure.figimage(logo, 1140, 137, zorder=1)
        elif map_.map_type == 'regional':
            ax.figure.figimage(logo, 1000, 137, zorder=1)
        elif map_.map_type == 'local':
            ax.figure.figimage(logo, 973, 137, zorder=1)
        else:
            ax.figure.figimage(logo, 1140, 181, zorder=1)

        # Plot the cities' information
        if map_.map_type is not 'tropical':
            for city in map_.cities:
                for max_temp, min_temp, per_chance_rain in zip(max_temperature_data, min_temperature_data, percent_chance_rain_data):
                    if round(city.lat, 1) == round(max_temp['lat'], 1) and round(city.lon, 1) == round(max_temp['lon'], 1):
                        ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
      
                        # City Name
                        if city.city_name == 'Pensacola' and map_.map_type == 'verywide':
                            ax.text(city.lon - 0.13, city.lat + 0.045, city.city_name, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                        elif map_.map_type == 'local':
                            ax.text(city.lon - 0.2, city.lat + 0.04, city.city_name, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                        else:
                            ax.text(city.lon - 0.45, city.lat + 0.07, city.city_name, fontsize='small', fontweight='bold',
                                    transform=ccrs.PlateCarree())

                        # City Min/Max Temperature
                        text = str(int(round(min_temp['value'] * 1.8 - 459.67))) + ' / ' + str(int(round(max_temp['value'] * 1.8 - 459.67)))
                        if map_.map_type == 'local':
                            ax.text(city.lon - 0.17, city.lat - 0.1, text, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                        else:
                            ax.text(city.lon - 0.34, city.lat - 0.175, text, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())

                        # City Percent Chance of Rain
                        text = str(int(round(per_chance_rain['value']))) + '%'
                        if map_.map_type == 'local':
                            ax.text(city.lon - 0.07, city.lat - 0.18, text, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                        else:
                            ax.text(city.lon - 0.2, city.lat - 0.36, text, fontsize='small',
                                    fontweight='bold',
                                    transform=ccrs.PlateCarree())
                        break

        plt.savefig('Day_{}_{}_DailyHighLowPerChanceRain.png'.format(day, map_.map_type))
        day += 1


def download_dataset():
    os.system('cd .. && cd DailyHighsLowsPerChanceOfRain_dataset_downloader && cd DailyHighsLowsPerChanceOfRain && cd spiders && scrapy '
              'crawl DailyHighLowPerChanceOfRain')
    return


if __name__ == '__main__':
    Utils.create_output_directory()
    main()
