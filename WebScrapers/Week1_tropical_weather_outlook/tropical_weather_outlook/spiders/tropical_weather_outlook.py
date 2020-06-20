import os
import re
import scrapy

class TropicalWeatherOutlook(scrapy.Spider):

    name = "tropical_weather_outlook"
    allowed_domains = ['www.nhc.noaa.gov']

    def start_requests(self):

        # Make the output folder
        self.make_output_directory()

        start_urls = [
            'https://www.nhc.noaa.gov/text/refresh/HFOTWOCP+shtml/061135_HFOTWOCP.shtml',
            'https://www.nhc.noaa.gov/text/refresh/MIATWOAT+shtml/061143_MIATWOAT.shtml',
            'https://www.nhc.noaa.gov/text/refresh/MIATWDAT+shtml/061024_MIATWDAT.shtml',
            'https://www.nhc.noaa.gov/text/refresh/MIATWDEP+shtml/060905_MIATWDEP.shtml',
            'https://www.nhc.noaa.gov/text/refresh/MIATWOEP+shtml/061120_MIATWOEP.shtml',
        ]

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        '''
        @param response: url (scrapy Repsonse object)
        @return report: scraped, formatted text from intended section of the url HTML

        For each url, scrape the title and the center text box. The text is under a div
        with class name "textproduct".
        '''

        # Grabs the title of the report
        title = response.css('h2::text').get()
        title = str(title)

        # Grabs all the text from the report
        text = response.xpath('/html/body/div[5]/div/div[2]/div/pre').get()
        text = str(text)

        # Delete all the exposed <* /> tags in the text
        text = re.sub('<.*?>', '', text)

        # Create the report titled with the current webpage's title (i.e. Atlantic Tropical Weather Outlook)
        report_title = title + ".txt"
        report = open(report_title, 'w+')

        # Create the body of the report
        body = title + text

        # Write the information to the report file
        report.write(body)
        report.close()

    def make_output_directory(self):
        '''
        If the "output" folder has not been created, create it.
        Then, have the program know to put the .txt files in the "output" folder.
        '''

        if not os.path.exists('output'):
            os.mkdir('output')
        os.chdir('output')
