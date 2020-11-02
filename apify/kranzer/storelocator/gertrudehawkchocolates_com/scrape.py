import csv
import re
from lxml import html
import requests
from w3lib.html import remove_tags
import base

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.gertrudehawkchocolates.com/find-a-store"
        cities = list(set([x for x in html.fromstring(requests.get(base_url).text).xpath('//select[@name="city"]/option/@value') if x]))
        for city in cities:
            city_url = base_url+"?state=&city={}&zip=&distance=5".format(city.replace(' ', '+'))
            locations = html.fromstring(requests.get(city_url).text)
            index = 0
            for location in locations.xpath('//div[@class="location-details"]'):
                l_data = [remove_tags(s.replace('\r\n','')).rstrip().strip() for s in location.xpath('./p/text()')]
                item = base.Item(location)
                item.add_value('locator_domain', city_url)
                if not l_data[0][0].isdigit():
                    item.add_value('location_name', l_data[0])
                    del l_data[0]
                    item.add_value('street_address', l_data[0])
                    del l_data[0]
                else:
                    item.add_value('street_address', l_data[0])
                    del l_data[0]
                if not l_data[0].startswith(city):
                    del l_data[0]
                d = re.match(r'(?P<city>.+?)\s,(?P<state>[A-Z][A-Z])(\s(?P<zip>.+))?', l_data[0]).groupdict()
                del l_data[0]
                if d.get('city'):
                    item.add_value('city', d['city'])
                if d.get('state'):
                    item.add_value('state', d['state'])
                if d.get('zip'):
                    item.add_value('zip', d['zip'])
                item.add_value('country_code', 'US')
                if '-' in l_data[0]:
                    item.add_value('phone', l_data[0])
                script = ''.join(locations.xpath('//script/text()')).replace('\r','').replace('\n','').replace('\t','')
                try:
                    lat, lng = re.findall(r'newLatLng = new google\.maps\.LatLng\((?P<lat>.+?),(?P<lng>.+?)\);', script)[index]
                    item.add_value('latitude', lat)
                    item.add_value('longitude', lng)
                except:
                    pass
                index+=1
                yield item


if __name__ == '__main__':
    s = Scrape()
    s.run()
