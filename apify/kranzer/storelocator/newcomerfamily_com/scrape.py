import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []

class Scrape(base.Spider):

    def get_centroid_map(self, text):
        centroid_map = {}
        try:
            m = re.findall(r'(1d(-.+?)!2d(.+))', text)
            if m:
                m_ = [s for s in m[0] if s]
                if m_:
                    return {"1": (m_[2][:m_[2].find('!')], m_[1][:m_[1].find('!')])}
            else:
                m = re.findall(r'(3d(.+?)!4d(-.+))|(@(.+?),(.+?),)|(sll=(.+?),(.+?)&)', text)
                if m:
                    m_ = [s for s in m[0] if s]
                    if m_:
                        return {"1": (m_[1], m_[2])}
                else:
                    return {}
        except:
            return {}

    def crawl(self):
        base_url = "https://www.newcomerfamily.com"
        body = html.fromstring(requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).text).xpath('//div[@id="homeLocation"]//a/@href')
        for result in body:
            selector = base.selector(urljoin(base_url, result), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            for sel in selector['tree'].xpath('//div[contains(@class, "locationcontainer")]//div[@class="chapel-text"]'):
                i = base.Item(sel)
                centroid_map = self.get_centroid_map(sel.xpath('./div[@class="row"][2]//a[contains(@href, "google")]/@href')[0])
                i.add_value('locator_domain', base_url)
                i.add_xpath('page_url', './div[@class="row"][1]//a/@href', base.get_first, lambda x: urljoin(selector['url'], x))
                i.add_xpath('location_name', './div[@class="row"][1]//a/text()', base.get_first)
                i.add_xpath('phone', './div[@class="row"]//a/@href[contains(., "tel:")]', base.get_first, lambda x: x.replace('tel:',''))
                loc = [s.replace('\n','').replace('\r','').strip() for s in sel.xpath('./div[@class="row"][last()-1]//text()') if s.replace('\n','').replace('\r','').strip()]
                if loc:
                    tup = re.findall(r'(.+?),?\s([A-Z]+|California),?\s(\d+)', loc[-1].replace('\r','').strip())
                    if tup:
                        i.add_value('city', tup[0][0])
                        i.add_value('state', tup[0][1])
                        i.add_value('zip', tup[0][2])
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    i.add_value('street_address', loc[:-1], lambda x: ', '.join(x))
                i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
                i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
                crawled_val = i.as_dict()['page_url'].split('location/')[1]
                if crawled_val not in crawled:
                    crawled.append(crawled_val)
                    yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
