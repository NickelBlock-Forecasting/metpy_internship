import urllib.error
import urllib.request

import scrapy


class SPC_CPC_dataset_downloader(scrapy.Spider):
    name = "SPC_CPC_dataset_downloader"

    def start_requests(self):
        start_urls = [
            'https://tds.scigw.unidata.ucar.edu/thredds/catalog/grib/NCEP/NDFD/SPC/CONUS/latest.html',  # SPC
            'https://tds.scigw.unidata.ucar.edu/thredds/catalog/grib/NCEP/NDFD/CPC/CONUS/latest.html',  # CPC
        ]

        yield scrapy.Request(start_urls[0], callback=self.parse, meta={'start_url': start_urls[0]})
        yield scrapy.Request(start_urls[1], callback=self.parse, meta={'start_url': start_urls[1]})


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
        if 'SPC' in download_link:
            dataset_type = 'SPC_data'
        elif 'CPC' in download_link:
            dataset_type = 'CPC_data'

        try:
            urllib.request.urlretrieve(download_link, '../../../output/{}.grb2'.format(dataset_type))
        except urllib.error.URLError:
            print('Dataset download link not found.')
