import re

import base
from urllib.parse import urljoin
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bankwithunited_com')



class Scrape(base.Spider):
    def crawl(self):
        base_url = "https://www.bankwithunited.com/contact-us"
        locations = base.selector(base_url)
        for location in locations['tree'].xpath('//div[@class="geolocation"]'):
            i = base.Item(location)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('location_name', './/div[@class="location-content"]/*[contains(@class, "branch-name")]/*/text()', lambda x: [s.replace('\n','') for s in x if s.strip()], base.get_first, lambda x: x[:-1] if x[-1]==',' else x)
            i.add_xpath('city', './/div[@class="location-content"]/*[contains(@class, "address-locality")]/*/text()', lambda x: [s.replace('\n','').strip() for s in x if s.strip()], base.get_first, lambda x: x[:-1] if x[-1]==',' else x)
            i.add_xpath('state', './/div[@class="location-content"]/*[contains(@class, "address-administrative-area")]/*/text()', lambda x: [s.replace('\n','') for s in x if s.strip()], base.get_first, lambda x: x[:-1] if x[-1]==',' else x, lambda x: base.get_state_code(x))
            i.add_xpath('zip', './/div[@class="location-content"]/*[contains(@class, "address-postal-code")]/*/text()', lambda x: [s.replace('\n','') for s in x if s.strip()], base.get_first)
            i.add_xpath('phone', './/div[@class="location-content"]/*[contains(@class, "phone-number")]/*/a[contains(@href, "tel")]/text()', lambda x: [s for s in x if s.strip()], base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('street_address',
                        './/div[@class="location-content"]/*[contains(@class, "address-line1")]/*/text()',
                        lambda x: [s.replace('\n', '') for s in x if s.strip()],
                        base.get_first,
                        lambda x: x[:x.find(', '+i.as_dict()['city'])] if ', '+i.as_dict()['city'] in x else x)

            i.add_xpath('longitude', './span/meta[@property="longitude"]/@content', base.get_first)
            i.add_xpath('latitude', './span/meta[@property="latitude"]/@content', base.get_first)
            logger.info(i)
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
