import os
import scrapy
import urllib.request


class DailyHighsLowsPerChanceOfRain(scrapy.Spider):
    name = "DailyHighsLowsPerChanceOfRain"

    def start_requests(self):
        start_urls = [
            'https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod/',
        ]

        yield scrapy.Request(start_urls[0], callback=self.parse, cb_kwargs={'start_url': start_urls[0]})

    def parse(self, response, start_url):
        # Find all links
        links = response.css('pre a::text').getall()
        yesterday = links[1]
        url = start_url + yesterday

        if scrapy.Request(url, callback=self.check_for_data):
            yield scrapy.Request(url, callback=self.next_page,
                                 cb_kwargs={'url': url, 'hour': '12/', 'day': 'yesterday'})
        else:
            print('Forecast hour 12 UTC is missing.')

    def check_for_data(self, response):
        links = response.css('pre a::text').getall()
        if '12/' not in links:
            return False
        elif '12/' in links:
            return True

    def next_page(self, response, url, hour, day):
        yield dict(
            url=url,
            hour=hour,
            day=day
        )
        # Find all links,  grab the latest link, update the url
        # links = response.css('pre a::text').getall()
        try:
            url = url + hour + 'grib2/'
            yield scrapy.Request(url, callback=self.get_download_links, cb_kwargs={'url': url, 'day': day})
        except:
            print('Error finding grib2/ link. Try re-running the script in a few minutes.')

    def get_download_links(self, response, url, day):
        yield dict(
            url=url,
            day=day
        )

        '''
            The way the forecast hours are processes is the following. The lists are backwards for each day.
            When looping through, first we want to grab the exact hour # for each day (i.e. 24, 48, 72, 96, etc.),
            but sometimes that exact hour is not in the data. So, we try to find -1 the hour # (i.e. 23, 47, 71, etc.)
            instead. If we can't find that hour # as well, we try the hour # +1 (i.e. 25, 49, 73, etc.),
            and keep adding 1 until we hit the hour count. It isn't perfect, but it catches the majority of
            behaviors from the webpage that has missing data hours.
        '''
        forecast_hours = {
            'Day0': ['f028.co', 'f027.co', 'f026.co', 'f025.co', 'f023.co', 'f024.co'],
            'Day1': ['f052.co', 'f051.co', 'f050.co', 'f049.co', 'f047.co', 'f048.co'],
            'Day2': ['f076.co', 'f075.co', 'f074.co', 'f073.co', 'f071.co', 'f072.co'],
            'Day3': ['f100.co', 'f099.co', 'f098.co', 'f097.co', 'f095.co', 'f096.co'],
            'Day4': ['f124.co', 'f123.co', 'f122.co', 'f121.co', 'f119.co', 'f120.co'],
            'Day5': ['f148.co', 'f147.co', 'f146.co', 'f145.co', 'f143.co', 'f144.co'],
            'Day6': ['f172.co', 'f171.co', 'f170.co', 'f169.co', 'f167.co', 'f168.co'],
            'Day7': ['f196.co', 'f195.co', 'f194.co', 'f193.co', 'f191.co', 'f192.co'],
            'Day8': ['f220.co', 'f219.co', 'f218.co', 'f217.co', 'f215.co', 'f216.co'],
            'Day9': ['f244.co', 'f243.co', 'f242.co', 'f241.co', 'f239.co', 'f240.co'],
            'Day10': ['f258.co', 'f260.co', 'f261.co', 'f262.co', 'f263.co', 'f264.c0'],
        }

        # Grabs the text from all the links
        links = response.css('pre a::text').getall()

        download_links = []

        # Loop through the forecast_hours Key-Values, Matching the values with the correct links for download
        for key, value in forecast_hours.items():
            dl_link = 0
            for i in range(len(value)):
                for link in links:
                    if value[i] in link:
                        dl_link = url + link
                        break
            if dl_link in download_links:
                continue
            download_links.append(dl_link)

        # Should be 11 items for 10 days, plus yesterday. If it is not 10 items, days are missing.
        if len(download_links) == 11:
            for d in download_links:
                print(d)
            self.download_data(download_links)
        else:
            print('NOT ALL DAYS INCLUDED IN DATA. IF PROBLEM PERSISTS, WAIT A FEW MINS. BEFORE RE-RUNNING COMMAND.')

    def download_data(self, urls):
        self.make_output_dir()
        for i in range(len(urls)):
            print("Downloading file: ", urls[i])
            urllib.request.urlretrieve(urls[i], os.getcwd() + '/Day_{}_data.grb2'.format(i))

    def make_output_dir(self):
        if not os.path.exists('output'):
            os.mkdir('output')
        os.chdir('output')

