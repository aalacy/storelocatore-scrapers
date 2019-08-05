
import base
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.gerbercollision.com"
        states_provs = base.selector(urljoin(base_url,'/locations'))
        for state_url in states_provs['tree'].xpath('//div[@class="row"]/div/a/@href[contains(., "/locations/")]'):
            state = base.selector(urljoin(states_provs['request'].url,state_url))
            pagination = state['tree'].xpath('(//ul[contains(@class, "pagination")])[1]/li/a/@href')
            yield from self.get_item(state)
            if pagination:
                del pagination[0]
                for p in pagination:
                    state = base.selector(urljoin(state['request'].url,p))
                    yield from self.get_item(state)

    def get_item(self, state):
        for loc_url in state['tree'].xpath('//div[contains(@style, "image")]/a'):
            location = base.selector(urljoin(state['request'].url, loc_url.xpath('./@href')[0]))
            if location['request'].status_code == 200:
                i = base.Item(location['tree'])
                i.add_value('locator_domain', location['url'])
                i.add_xpath('location_name', '//h1[@itemprop="name"]/text()', base.get_first)
                i.add_xpath('street_address', '//div[@class="address"]//span[@itemprop="streetAddress"]/text()',
                            base.get_first)
                i.add_xpath('city', '//div[@class="address"]//span[@itemprop="addressLocality"]/text()', base.get_first)
                i.add_xpath('state', '//div[@class="address"]//span[@itemprop="addressRegion"]/text()', base.get_first)
                i.add_xpath('zip', '//div[@class="address"]//span[@itemprop="postalCode"]/text()', base.get_first)
                i.add_value('country_code', base.get_country_by_code(i.as_dict().get('state')))
                i.add_xpath('phone', '//div[@class="phones"]//span[@itemprop="telephone"]/text()', base.get_first)
                # print(loc_url.xpath('./div/@data-lat'))
                i.add_value('latitude', loc_url.xpath('./div/@data-lat'), lambda x: [s for s in x if s], base.get_first)
                i.add_value('longitude', loc_url.xpath('./div/@data-lng'), lambda x: [s for s in x if s], base.get_first)
                i.add_value('hours_of_operation', ';'.join(
                    ['- '.join(s.xpath('.//text()')) for s in location['tree'].xpath('//div[@class="timesheet"]/p')]))
                yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
