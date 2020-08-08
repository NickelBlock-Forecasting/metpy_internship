import argparse
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import pygrib
import numpy as np

import Map_Info as map_info


def download_dataset():
    os.system('cd .. && cd SPC_CPC_dataset_downloader && cd SPC_CPC_dataset_downloader && cd spiders && scrapy '
              'crawl SPC_CPC_dataset_downloader')
    return


def main():
    # download_dataset()

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='Which type of map to be generated.')
    args = parser.parse_args()

    if args.map == 'verywide':
        map_ = map_info.VeryWide()
    elif args.map == 'regional':
        map_ = map_info.Regional()
    elif args.map == 'local':
        map_ = map_info.Local()
    elif args.map == 'country':
        map_ = map_info.Country()

    # Open dataset and capture relevant info
    file = '../output/SPC_data.grb2'
    dataset = pygrib.open(file)
    data = pygrib.open(file)

    valid_days_data = get_valid_days(dataset, data)

    for data in valid_days_data:
        print(data.validDate)
        lats, lons = data.latlons()
        values = data.values

        # Create the figure for graphing
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(map_.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())

        # Add boundaries to plot
        ax.add_feature(cfeature.OCEAN, facecolor=cfeature.COLORS['water'])
        if map_.map_type == 'verywide':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
        elif map_.map_type == 'regional' or map_.map_type == 'local':
            ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
            reader = shpreader.Reader('../county_data/countyl010g.shp')
            counties = list(reader.geometries())
            COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
            ax.add_feature(COUNTIES, facecolor='none', edgecolor='black', linewidth=0.3)
        elif map_.map_type == 'tropical' or map_.map_type == 'country':
            countries = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_0_countries',
                scale='50m',
                facecolor='none')
            ax.add_feature(cfeature.LAND)
            ax.add_feature(countries, edgecolor='black', linewidth=0.5)

        # Contour temperature at each lat/long
        cf = ax.contourf(lons, lats, values,
                         levels=[0, 1, 2, 3, 4, 5],
                         extend='both',
                         transform=ccrs.PlateCarree(),
                         cmap='Greens')

        # Plot all the cities
        if map_.map_type is not 'tropical' or map_.map_type is not 'country':
            for city in map_.cities:
                ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())
                ax.text(city.lon - 0.5, city.lat + 0.09, city.city_name, fontsize='small', fontweight='bold',
                        transform=ccrs.PlateCarree())

        # Make a title with the time value
        time = str(data.validDate)
        ax.set_title('SPC Categorical Outlook for ' + time + ' UTC',
                     fontsize=12, loc='left')

        # Company copyright on the bottom right corner
        SOURCE = 'NickelBlock Forecasting'
        text = AnchoredText(r'$\mathcircled{{c}}$ {}'
                            ''.format(SOURCE),
                            loc=4, prop={'size': 9}, frameon=True)
        data_model = AnchoredText('SPC Probabilistic to Categorical Outlook model', loc=3, prop={'size': 9}, frameon=True)
        ax.add_artist(data_model)
        ax.add_artist(text)

        # Plot a colorbar to show temperature and reduce the size of it
        plt.colorbar(cf, ax=ax, fraction=0.032)

        plt.savefig('SPC_{}_Map.png'.format(str(data.validDate)))


def get_valid_days(dataset_copy_1, dataset_copy_2):
    days = []
    final_days = []

    # Getting unique days, ignoring duplicate dates
    for dp in dataset_copy_1:
        if dp.validDate in days:
            continue
        else:
            days.append(dp.validDate)

    # Match the dates with the respective data points in the dataset
    for day in days:
        for dp in dataset_copy_2:
            if day == dp.validDate:
                final_days.append(dp)
                break
    return final_days


def make_output_directory():
    if not os.path.exists('output'):
        os.mkdir('output')
    os.chdir('output')


if __name__ == '__main__':
    make_output_directory()
    main()
