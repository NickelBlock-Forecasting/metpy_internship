import argparse
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import pygrib

import Map_Info as map_info


def download_dataset():
    os.system('cd .. && cd DailyHighsLowsPerChanceOfRain && cd DailyHighsLowsPerChanceOfRain && cd spiders && scrapy '
              'crawl DailyHighLowPerChanceOfRain')
    return


def main():
    download_dataset()

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    args = parser.parse_args()

    if args.map == 'verywide':
        map_ = map_info.VeryWide()
    elif args.map == 'regional':
        map_ = map_info.Regional()
    elif args.map == 'local':
        map_ = map_info.Local()

    # Open dataset and capture relevant info
    file = '../output/DHLPCoR_data.grb2'
    data = pygrib.open(file)
    max_temp = data.select(name='Maximum temperature')
    min_temp = data.select(name='Minimum temperature')
    per_chance_rain = data.select(name='Probability of 0.01 inch of precipitation (POP)')

    # loops Day by day (1-5)
    day = 1
    for max_t, min_t, per_chance in zip(max_temp, min_temp,  per_chance_rain):
        # Max Temperature data
        max_temp_data = []
        max_temp_lats, max_temp_lons = max_t.latlons()
        max_temp_values = max_t.values
        for lat, lon, val in zip(max_temp_lats, max_temp_lons, max_temp_values):
            for la, lo, va in zip(lat, lon, val):
                max_temp_data.append({'lat': la, 'lon': lo, 'value': va})

        # Min Temperature data
        min_temp_data = []
        min_temp_lats, min_temp_lons = min_t.latlons()
        min_temp_values = min_t.values
        for lat, lon, val in zip(min_temp_lats, min_temp_lons, min_temp_values):
            for la, lo, va in zip(lat, lon, val):
                min_temp_data.append({'lat': la, 'lon': lo, 'value': va})

        # Percent chance of rain data
        percent_chance_rain_data = []
        per_chance_rain_lats, per_chance_rain_lons = per_chance.latlons()
        per_chance_rain_values = per_chance.values
        for lat, lon, val in zip(per_chance_rain_lats, per_chance_rain_lons, per_chance_rain_values):
            for la, lo, va in zip(lat, lon, val):
                percent_chance_rain_data.append({'lat': la, 'lon': lo, 'value': va})

        # Create the figure for graphing
        fig = plt.figure(figsize=(10, 7))
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
        ax.set_title('Daily High / Low / Percent Chance of Rain taken ' + str(max_t.validDate)[:-9] + ' UTC',
                     fontsize=12, loc='left')
        SOURCE = 'NickelBlock Forecasting'
        text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                            ''.format(SOURCE),
                            loc=4, prop={'size': 9}, frameon=True)
        data_model = AnchoredText('NWS/NDFD CONUS model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)
        ax.add_artist(text)

        # Plot the cities' information
        if map_.map_type is not 'tropical':
            for city in map_.cities:
                for max, min, per_chance_rain in zip(max_temp_data, min_temp_data, percent_chance_rain_data):
                    if round(city.lat, 1) == round(max['lat'], 1) and round(city.lon, 1) == round(max['lon'], 1):
                        ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
                        # City Name
                        ax.text(city.lon - 0.60, city.lat + 0.07, city.city_name, fontsize='small', fontweight='bold',
                                transform=ccrs.PlateCarree())

                        # City Min/Max Temperature
                        text = str(int(round(min['value'] * 1.8 - 459.67))) + ' / ' + str(int(round(max['value'] * 1.8 - 459.67)))
                        ax.text(city.lon - 0.4, city.lat - 0.24, text, fontsize='small',
                                fontweight='normal',
                                transform=ccrs.PlateCarree())

                        # City Percent Chance of Rain
                        text = str(int(round(per_chance_rain['value']))) + '%'
                        ax.text(city.lon - 0.2, city.lat - 0.47, text, fontsize='small',
                                fontweight='normal',
                                transform=ccrs.PlateCarree())
                        break

        plt.savefig('Day_{}_{}_DailyHighLowPerChanceRain.png'.format(day, map_.map_type))
        day += 1


def make_output_directory():
    if not os.path.exists('output'):
        os.mkdir('output')
    os.chdir('output')


if __name__ == '__main__':
    make_output_directory()
    main()

