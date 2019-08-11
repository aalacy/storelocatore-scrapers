import re
import time
import usaddress
from lxml import html
import base
import requests, json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scrape(base.Spider):
    def crawl(self):
        base_url = "https://www.phoenix.edu/campus-locations.html"
        for result in html.fromstring(requests.get(base_url).text).xpath('///div[@class="dummyclass"]/a/@href'):
            selector = base.selector(urljoin(base_url,result))
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', selector['url'])
            i.add_xpath('hours_of_operation', '//div[@class="tabindexClass"]/p/text()[contains(., "Hours:")]', base.get_first, lambda x: x.replace('Hours: ', ''))
            loc = selector['tree'].xpath('//p[@class="section-lead-copy"]//text()')
            if loc.index('Phone: ') == 2:
                i.add_value('street_address', loc[0])
                st = loc[1].split(',')


            else:
                i.add_value('street_address', loc[:2], lambda x: ', '.join(x))
                st = loc[2].split(',')
            if len(st) == 2:
                st_temp = [s for s in st[1].split(' ') if s]
                st = [st[0]]
                st += st_temp
            i.add_value('city', st[0], lambda x: x.strip())
            i.add_value('state', st[1], lambda x: x.strip())
            i.add_value('zip', st[2], lambda x: x.strip())
            i.add_value('phone', loc[-1])
            i.add_xpath('location_name', '//h2[@id="contentParsys_row_hero"]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('latitude', "<INACCESSIBLE>")
            i.add_value('longitude', "<INACCESSIBLE>")
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
