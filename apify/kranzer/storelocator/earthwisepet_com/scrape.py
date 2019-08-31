
import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://earthwisepet.com/store-locator"
        body = html.fromstring(requests.get(base_url).text)
        for result in body.xpath('//div[@class="store"]/div[@class="address"]/div[@class="store-link"]/div/a[1]/@href'):
            selector = base.selector(urljoin(base_url,result))
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', selector['url'])
            i.add_xpath('location_name', './/meta[@property="og:locality"]/@content', base.get_first)
            i.add_xpath('street_address', './/meta[@property="og:street_address"]/@content', base.get_first)
            i.add_xpath('city', './/meta[@property="og:locality"]/@content', base.get_first)
            i.add_xpath('state', './/meta[@property="og:region"]/@content', base.get_first)
            i.add_xpath('zip', './/meta[@property="og:postal_code"]/@content', base.get_first)
            i.add_xpath('phone', './/meta[@property="og:phone_number"]/@content', base.get_first)
            i.add_xpath('longitude', './/meta[@property="og:longitude"]/@content', base.get_first)
            i.add_xpath('latitude', './/meta[@property="og:latitude"]/@content', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('hours_of_operation', '//div[preceding-sibling::h2[1][contains(text(), "Hours")]]//span[@class="oh-display"]//text()', lambda x: [s_.strip() for s_ in x if s_],lambda x: '; '.join([' '.join(x) for x in zip(x[0::2], x[1::2])]).replace('\n', '').strip(), lambda x: x[2:] if x.startswith('; ') else x)
            if i.as_dict() not in crawled and "coming soon" not in i.as_dict()['street_address'].lower():
                crawled.append(i.as_dict())
                yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
