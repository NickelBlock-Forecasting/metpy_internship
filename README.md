# NickelBlock Internship
All the code for the NickelBlock internship.

Map Generators [ Week 2 ]
==
To generate temperature or precipitation maps for week 2, use the following command:

```
python [Map File] -m [Map Type] -t [hours]
```

Where the `Map File` is the script to run, `-m` is the flag for map type, `-t` is the flag for time, and `hours` is how many hours from the time of running the script you want to generate the map.

All Map Types include: `verywide` , `regional` , `local` , `tropical`

Temperature
==
Example that generates a very wide temperature map 12 hours from now:

```
python Temp_Map_Generator.py -m verywide -t 12
```

Precipitation
==
Example that generates local precipitation rate map 12 hours from now:

```
python Precip_Map_Generator.py -m local -t 12
```


Daily Highs/Lows Percent Chance of Rain [ Week 3 ]
==
To run the webscraper, use the following command inside 'spider' folder:

```
scrapy crawl DailyHighsLowsPerChanceOfRain
```

The datasets should all be downloaded in the output folder, ready to be processed.

Note: Sometimes the command can fail, due to missing datasets or otherwise. If this happens, wait a few mins to an hour to re-run.
These issues are being worked on, and fail safes are present in the code.
