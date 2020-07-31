# NickelBlock Internship
All the code for the NickelBlock internship.

Map Generators (Temperature, Precipitation, Daily High/Low/PercentChanceRain)
==
To generate temperature or precipitation maps navigate to the 'MapGenerators' folder and use the following command:

```
python [Map File] -m [Map Type] -t [hours]
```

Where the `Map File` is the script to run, `-m` is the flag for map type, `-t` is the flag for time, and `hours` is how many hours from the time of running the script you want to generate the map.

All Map Types include: `verywide` , `regional` , `local` , `tropical`

Temperature
--
Example that generates a very wide temperature map 12 hours from now:

```
python Temp_Map_Generator.py -m verywide -t 12
```

Precipitation
--
Example that generates local precipitation rate map 12 hours from now:

```
python Precip_Map_Generator.py -m local -t 12
```

Daily Highs / Lows / Percent Chance of Rain
--
To generate maps with daily highs/lows/percent chance of rain maps, navigate to the 'MapGenerators' folder, and use the following command:

```
python DailyHighsLowsPerChanceOfRain_Map_Generator.py -m [Map Type]
```

The command should create and save maps for 5 days in advance, putting the maps in the output folder.

Example that generates regional daily H/L/PCoR maps:

```
python DailyHighsLowsPerChanceOfRain_Map_Generator.py -m regional
```
