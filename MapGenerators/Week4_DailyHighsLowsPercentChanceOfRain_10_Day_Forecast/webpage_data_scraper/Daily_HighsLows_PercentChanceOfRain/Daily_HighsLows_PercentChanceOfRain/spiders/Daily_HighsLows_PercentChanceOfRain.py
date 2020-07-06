import os
import re
import scrapy
import urllib.request


class DailyHighsLowsPerChanceOfRain(scrapy.Spider):

    name = "DailyHighsLowsPerChanceOfRain"

    def start_requests(self):
        start_urls = [
            'https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod/',
        ]

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={'start_url': start_urls[0]})

    def parse(self, response, start_url):
        # Find all links,  grab the latest link, update the url
        links = response.css('pre a::text').getall()
        latest_link = links[-1]
        url = start_url + latest_link

        yield scrapy.Request(url, callback=self.next_page, cb_kwargs={'url': url})

    def next_page(self, response, url):
        yield dict(
            url=url
        )
        # Find all links,  grab the latest link, update the url
        links = response.css('pre a::text').getall()

        # If the latest day does NOT have a 'grib2/' path, grab the previous day
        try:
            latest_link = links[-1]
            url = url + latest_link + 'grib2/'
            yield scrapy.Request(url, callback=self.get_download_links, cb_kwargs={'url': url})
        except:
            latest_link = links[-2]
            url = url + latest_link + 'grib2/'
            yield scrapy.Request(url, callback=self.get_download_links, cb_kwargs={'url': url})

    def get_download_links(self, response, url):
        yield dict(
            url=url
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
            'Day1': ['f028.co', 'f027.co', 'f026.co', 'f025.co', 'f023.co', 'f024.co'],
            'Day2': ['f052.co', 'f051.co', 'f050.co', 'f049.co', 'f047.co', 'f048.co'],
            'Day3': ['f076.co', 'f075.co', 'f074.co', 'f073.co', 'f071.co', 'f072.co'],
            'Day4': ['f100.co', 'f099.co', 'f098.co', 'f097.co', 'f095.co', 'f096.co'],
            'Day5': ['f124.co', 'f123.co', 'f122.co', 'f121.co', 'f119.co', 'f120.co'],
            'Day6': ['f148.co', 'f147.co', 'f146.co', 'f145.co', 'f143.co', 'f144.co'],
            'Day7': ['f172.co', 'f171.co', 'f170.co', 'f169.co', 'f167.co', 'f168.co'],
            'Day8': ['f196.co', 'f195.co', 'f194.co', 'f193.co', 'f191.co', 'f192.co'],
            'Day9': ['f220.co', 'f219.co', 'f218.co', 'f217.co', 'f215.co', 'f216.co'],
            'Day10': ['f244.co', 'f243.co', 'f242.co', 'f241.co', 'f239.co', 'f240.co'],
        }

        # Grabs the text from all the links
        links = response.css('pre a::text').getall()

        download_links = []

        # Loop through the forecast_hours Key-Values, Matching the values with the correct links for download
        for key, value in forecast_hours.items():
            for i in range(len(value)):
                for link in links:
                    if value[i] in link:
                        dl_link = url + link
                        break
            if dl_link in download_links:
                continue
            download_links.append(dl_link)

        # Should be 10 items for 10 days. If it is not 10 items, days are missing.
        if len(download_links) == 10:
            for d in download_links:
                print(d)
            self.download_data(download_links)
        else:
            print('NOT ALL DAYS INCLUDED IN DATA. IF PROBLEM PERSISTS, WAIT A FEW MINS. BEFORE RE-RUNNING COMMAND.')

    def download_data(self, urls):
        self.make_output_dir()
        for i in range(len(urls)):
            print("Downloading file: ", urls[i])
            urllib.request.urlretrieve(urls[i], os.getcwd() + '/Day_{}_data.grb2'.format(i+1))

    def make_output_dir(self):
        if not os.path.exists('output'):
            os.mkdir('output')
        os.chdir('output')
