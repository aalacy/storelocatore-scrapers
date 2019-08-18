import re

import base
import usaddress
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.usaveinclinics.com"
        locations = base.selector(urljoin(base_url,'/locations'))
        for location_url in locations['tree'].xpath('//div[@class="location-listing__buttons"]/a[1]/@href'):
            location = base.selector(location_url)
            if not location['tree'].xpath('//span[@class="breadcrumb_last"][contains(text(), "Coming Soon")]'):
                print(location_url)
                i = base.Item(location['tree'])
                i.add_value('locator_domain', location['url'])
                i.add_xpath('location_name', '//h1[@class="masthead__heading"]/text()', base.get_first)
                i.add_xpath('street_address', '(//aside[contains(@class, "location-info")])[1]/div[@class="location-info__item"][1]/text()[3]',
                            base.get_first, lambda x: x.strip())
                addr = usaddress.parse(location['tree'].xpath('(//aside[contains(@class, "location-info")])[1]/div[@class="location-info__item"][1]/text()[4]')[0])
                city = ' '.join([city[0] for city in addr if city[1] == "PlaceName"]).replace(',', '')
                try:
                    state = [state[0] for state in addr if state[1] == "StateName"][0].replace(',', '')
                    if state == 'US':
                        state = ''
                except:
                    state = ''
                try:
                    zip = [zip[0] for zip in addr if zip[1] == "ZipCode"][0].replace(',', '')
                    if len(zip) == 4:
                        zip = '0' + zip
                except:
                    zip = ''
                i.add_value('city', city)
                i.add_value('state', state)
                i.add_value('zip', zip)
                i.add_value('country_code', "US")
                i.add_xpath('phone', '(//aside[contains(@class, "location-info")])[1]/div[@class="location-info__item"][strong="Phone:"]/a/text()', base.get_first)
                script = location['tree'].xpath('//script[@type="application/ld+json"][contains(text(), "GeoCoordinates")]/text()')[0]
                try:
                    script = script.replace('\n','').replace('\r', '')
                    lat_lng = re.findall(r'"latitude":\s\"(?P<lat>.+?)\",.+\"longitude":\s\"(?P<lng>.+?)\"', script)

                    i.add_value('latitude', lat_lng[0][0])
                    i.add_value('longitude', lat_lng[0][1])
                except:
                    pass
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
