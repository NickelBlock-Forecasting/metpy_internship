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


def download_dataset():
    os.system('cd .. && cd SPC_CPC_dataset_downloader && cd SPC_CPC_dataset_downloader && cd spiders && scrapy '
              'crawl SPC_CPC_dataset_downloader')
    return


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
    elif args.map == 'tropical':
        map_ = map_utils.Tropical()
    elif args.map == 'country':
        map_ = map_utils.Country()

    # Open dataset and capture relevant info
    file = '../output/CPC_data.grb2'
    dataset = pygrib.open(file)

    # Grab the temperature and precipitation data from the dataset
    precipitation_data = []
    temperature_data = dataset.select(name='Temperature')
    for d in dataset:
        if str(d) not in str(temperature_data):
            precipitation_data.append(d)

    temperature_precipitation_data = {
        'Temperatures': temperature_data,
        'Precipitations': precipitation_data,
    }.items()

    for key, values in temperature_precipitation_data:
        fig = plt.figure(figsize=(15, 9))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        ax.set_extent(map_.NorthSouthEastWest[::-1], crs=ccrs.Geodetic())
        for value in values:
            lats, lons = value.latlons()
            vals = value.values
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
                ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)

            # Contour temperature value at each lat/lon depending on the key
            if 'event below' in str(value):
                if key == 'Temperatures':
                    # Contour temperature at each lat/long
                    cf = ax.contourf(lons, lats, vals,
                                     levels=[33, 40, 50, 60, 70, 80, 90],
                                     transform=ccrs.PlateCarree(),
                                     cmap='Blues')
                    cb1 = plt.colorbar(cf, ax=ax, orientation='horizontal', fraction=0.045, pad=0.04)
                elif key == 'Precipitations':
                    # Contour temperature at each lat/long
                    cf = ax.contourf(lons, lats, vals,
                                     levels=[33, 40, 50, 60, 70, 80, 90],
                                     transform=ccrs.PlateCarree(),
                                     cmap='Blues')
                    cb1 = plt.colorbar(cf, ax=ax, orientation='horizontal', fraction=0.035, pad=0.08)
                cb1.ax.set_xlabel('Probability of Below (%)')
            elif 'event above' in str(value):
                if key == 'Temperatures':
                    # Contour temperature at each lat/long
                    cf = ax.contourf(lons, lats, vals,
                                     levels=[33, 40, 50, 60, 70, 80, 90],
                                     transform=ccrs.PlateCarree(),
                                     cmap='Reds')
                    cb2 = plt.colorbar(cf, ax=ax, orientation='horizontal', fraction=0.0395, pad=0.08)
                elif key == 'Precipitations':
                    # Contour temperature at each lat/long
                    cf = ax.contourf(lons, lats, vals,
                                     levels=[33, 40, 50, 60, 70, 80, 90],
                                     transform=ccrs.PlateCarree(),
                                     cmap='Greens')
                    cb2 = plt.colorbar(cf, ax=ax, orientation='horizontal', fraction=0.0395, pad=0.04)
                cb2.ax.set_xlabel('Probability of Above (%)')

            # Plot all the cities
            if map_.map_type is not 'tropical' and map_.map_type is not 'country':
                for city in map_.cities:
                    ax.plot(city.lon, city.lat, 'ro', zorder=9, markersize=1.90, transform=ccrs.Geodetic())

                    if map_.map_type == 'local':
                        ax.text(city.lon - 0.3, city.lat + 0.04, city.city_name, fontsize='small', fontweight='bold',
                                transform=ccrs.PlateCarree())
                    else:
                        ax.text(city.lon - 0.5, city.lat + 0.09, city.city_name, fontsize='small', fontweight='bold',
                                transform=ccrs.PlateCarree())
            # Title
            ax.set_title('{} Probability for {} UTC'.format(key, str(value.validDate)),
                         fontsize=12, loc='left')

            # Company copyright bottom right corner
            text = AnchoredText('© NickelBlock Forecasting',
                                loc=4, prop={'size': 9}, frameon=True)
            ax.add_artist(text)

            # Data model
            data_model = AnchoredText('CPC Probability Outlook model', loc=3, prop={'size': 9}, frameon=True)
            ax.add_artist(data_model)

            # Add logo
            logo = Utils.get_logo()
            if map_.map_type == 'verywide':
                if key == 'Temperatures':
                    ax.figure.figimage(logo, 1040, 272, zorder=1)
                elif key == 'Precipitations':
                    ax.figure.figimage(logo, 1045, 265, zorder=1)
            elif map_.map_type == 'regional':
                if key == 'Temperatures':
                    ax.figure.figimage(logo, 925, 273, zorder=1)
                elif key == 'Precipitations':
                    ax.figure.figimage(logo, 930, 267, zorder=1)
            elif map_.map_type == 'local':
                if key == 'Temperatures':
                    ax.figure.figimage(logo, 904, 270, zorder=1)
                elif key == 'Precipitations':
                    ax.figure.figimage(logo, 909, 265, zorder=1)
            elif map_.map_type == 'tropical':
                if key == 'Temperatures':
                    ax.figure.figimage(logo, 1110, 272, zorder=1)
                elif key == 'Precipitations':
                    ax.figure.figimage(logo, 1115, 267, zorder=1)
            elif map_.map_type == 'country':
                if key == 'Temperatures':
                    ax.figure.figimage(logo, 1070, 271, zorder=1)
                elif key == 'Precipitations':
                    ax.figure.figimage(logo, 1075, 266, zorder=1)

        plt.savefig('CPC_{}_{}_Map.png'.format(key, value.validDate))


if __name__ == '__main__':
    Utils.create_output_directory()
    main()
