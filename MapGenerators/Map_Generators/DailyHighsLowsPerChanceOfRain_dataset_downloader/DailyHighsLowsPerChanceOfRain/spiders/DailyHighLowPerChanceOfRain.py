import urllib.error
import urllib.request

import scrapy


class DailyHighLowPerChanceOfRain(scrapy.Spider):
    name = "DailyHighLowPerChanceOfRain"

    def start_requests(self):
        start_url = 'https://tds.scigw.unidata.ucar.edu/thredds/catalog/grib/NCEP/NDFD/NWS/CONUS/NOAAPORT/latest.html'
        yield scrapy.Request(start_url, callback=self.parse, meta={'start_url': start_url})

    def parse(self, response):
        start_url = response.meta['start_url']
        link = response.css('tr td a::attr(href)').get()
        url = start_url.replace('latest.html', str(link))

        yield scrapy.Request(url, callback=self.download_data)

    def download_data(self, response):
        base_url = 'https://tds.scigw.unidata.ucar.edu'
        dl_links = response.css('html body ol li a::attr(href)').getall()
        for link in dl_links:
            if 'fileServer' in link:
                download_link = base_url + link
        try:
            urllib.request.urlretrieve(download_link, '../../../output/DHLPCoR_data.grb2')
        except urllib.error.URLError:
            print('Dataset download link not found.')
