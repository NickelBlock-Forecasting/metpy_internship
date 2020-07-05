# NickelBlock Internship
All the code for the NickelBlock internship.

Temperature Maps [ Week 2 ]
==
To generate temperature maps for week 2, use the following command:

```
python [Map File] -t [hours]
```

Where the `Map File` is the script to run, `-t` is the flag for time, and `hours` is how many hours from the time of 
running the script you want to generate a temperature map.

Example that generates local temperature map 12 hours from now:

```
python Map_Local_Temperature.py -t 12
```

Precipitation Maps [ Week 2 ]
==
To generate precipitation maps for week 2, use the following command:

```
python [Map File] -t [hours]
```

Example that generates local precipitation rate map 12 hours from now:

```
python Map_Local_Precipitation.py -t 12
```


Daily Highs/Lows Percent Chance of Rain [ Week 4 ]
==
To run the webscraper, use the following command inside 'spider' folder:

```
scrapy crawl DailyHighsLowsPerChanceOfRain
```

The datasets should all be downloaded in the output folder, ready to be processed.

Note: Sometimes the command can fail, due to missing datasets or otherwise. If this happens, wait a few mins to an hour to re-run.
These issues are being worked on, and fail safes are present in the code.
