# NickelBlock Internship

All the code for the NickelBlock internship.

## Environment setup

Please install Python 3.10 or 3.11 locally

Download and install Conda https://www.anaconda.com/download/

Use Conda to install required packages
cartopy - `conda install -c conda-forge cartopy`
siphon - `conda install -c conda-forge siphon`
netCDF4 - `conda install netCDF4`
opencv - `conda install -c conda-forge opencv`
pygrib - `conda install -c conda-forge pygrib`

# Map Generators (Temperature, Precipitation, Daily High/Low/PercentChanceRain, CPC Outlook, SPC Outlook)

To generate temperature or precipitation maps navigate to the 'MapGenerators' folder and use the following command:

```
python [Map File] -m [Map Type] -t [hours]
```

Where the `Map File` is the script to run, `-m` is the flag for map type, `-t` is the flag for time, and `hours` is how many hours from the time of running the script you want to generate the map.

All Map Types include: `verywide` , `regional` , `local` , `tropical`

## Temperature

Example that generates a very wide temperature map 12 hours from now:

```
python Temp_Map_Generator.py -m verywide -t 12
```

## Precipitation

Example that generates local precipitation rate map 12 hours from now:

```
python Precip_Map_Generator.py -m local -t 12
```

## Daily Highs / Lows / Percent Chance of Rain

To generate maps with daily highs/lows/percent chance of rain maps, navigate to the 'MapGenerators' folder, and use the following command:

```
python DailyHighsLowsPerChanceOfRain_Map_Generator.py -m [Map Type]
```

The command should create and save maps for 5 days in advance, putting the maps in the output folder.

Example that generates regional daily H/L/PCoR maps:

```
python DailyHighsLowsPerChanceOfRain_Map_Generator.py -m regional
```

## SPC Probabilistic Outlook

To generate SPC maps, navigate to the 'MapGenerators' folder, and use the following command:

```
python SPC_Map_Generator.py -m [Map Type]
```

The command will generate maps for all days present in the dataset, placing the map output in the output folder.

Example that generates country SPC maps:

```
python SPC_Map_Generator.py -m country
```
## CPC Probabilistic Outlook

To generate CPC maps, navigate to the 'MapGenerators' folder, and use the following command:

```
python CPC_Map_Generator.py -m [Map Type]
```

The command will generate maps for all days present in the dataset, placing the map output in the output folder.

Example that generates country CPC maps:

```
python CPC_Map_Generator.py -m country
```

# Map Examples

![Screen Shot 2020-08-19 at 8 02 00 PM](https://user-images.githubusercontent.com/45768739/90709100-0ca3fc00-e261-11ea-8136-96167cdc99e4.png)

![Screen Shot 2020-08-19 at 8 03 28 PM](https://user-images.githubusercontent.com/45768739/90709131-204f6280-e261-11ea-8df3-b64c8316e455.png)

![Screen Shot 2020-08-19 at 9 14 07 PM](https://user-images.githubusercontent.com/45768739/90709167-378e5000-e261-11ea-8976-fa9e68d13ca3.png)
