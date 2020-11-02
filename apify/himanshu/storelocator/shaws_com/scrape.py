import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time


session = SgRequests()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}

def write_output(data):
    with open('data.csv', mode='w',newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = locator_domain = "https://www.shaws.com/"
    r = session.get("https://local.shaws.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    page_link_list = []
    addresses=[]    
    for state_link in soup.find("ul",class_="Directory-listLinks").find_all("a",class_="Directory-listLink"):
        r1 = session.get("https://local.shaws.com/"+state_link["href"],headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        for city_link in soup1.find("ul",class_="Directory-listLinks").find_all("a",class_="Directory-listLink"):
            if city_link["data-count"] != "(1)" :
                a ="https://local.shaws.com/"+city_link["href"]
                r2= session.get(a,headers=headers)
                soup2 = BeautifulSoup(r2.text,"lxml")
                for ul in soup2.find("ul",class_="Directory-listTeasers Directory-row").find_all("a",class_="Teaser-titleLink"):
                    link = "https://local.shaws.com"+ul["href"].replace("..","").strip()
                    page_link_list.append(link)

            else:
                link = "https://local.shaws.com/"+city_link["href"]
                page_link_list.append(link)
    for page_url in page_link_list:
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        country_code = soup.find("div",class_="Core-address").find("address",class_="c-address")["data-country"]
        state = page_url.split("/")[3].strip().upper()
        city= page_url.split("/")[4].replace("-"," ").strip().capitalize()
        street_address = soup.find("address",class_="c-address").find_all("div",class_="c-AddressRow")[0].text.strip()
        phone = soup.find("div",{"itemprop":"telephone"}).text.strip()
        zipp = soup.find("span",{"itemprop":"postalCode"}).text.strip()
        latitude = soup.find("meta",{'itemprop':"latitude"})["content"]
        longitude = soup.find("meta",{'itemprop':"longitude"})["content"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        location_name = city
        hours_of_operation = " ".join(list(soup.find("table",class_="c-hours-details").stripped_strings)).replace("Day of the Week","").replace("Hours","").strip()
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        # attr = store[2] + " " + store[3]
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


# import re
# from string import capwords

# import base
# import ast
# import requests, json
# import asyncio
# import aiohttp
# from urllib.parse import urljoin
# from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shaws_com')


# base_url = "https://local.shaws.com/index.html"
# flatten = lambda l: [item for sublist in l for item in sublist]


# class Scrape(base.Spider):
#     crawled = set()
#     def normalize_days(self, text):
#         text = text.replace('Mo ', 'Mon ')
#         text = text.replace('Tu ', 'Tue ')
#         text = text.replace('We ', 'Wed ')
#         text = text.replace('Th ', 'Thu ')
#         text = text.replace('Fr ', 'Fri ')
#         text = text.replace('Sa ', 'Sat ')
#         text = text.replace('Su ', 'Sun ')
#         return text

#     async def _fetch_store(self, session, url):
#         async with session.get(url, timeout=60 * 60) as response:
#             resp = await response.text()
#             res_sel = html.fromstring(resp)
#             i = base.Item(res_sel)
#             i.add_value('locator_domain', base_url)
#             i.add_value('page_url', url)
#             i.add_xpath('location_name', './/span[@class="LocationName"]/span[@class="LocationName-geo"]/text()', base.get_first)
#             i.add_xpath('phone', './/span[@id="telephone"]/text()', base.get_first)
#             i.add_xpath('latitude', '//meta[@itemprop="latitude"]/@content', base.get_first)
#             i.add_xpath('longitude', '//meta[@itemprop="longitude"]/@content', base.get_first)
#             lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
#             i.add_xpath('city', '//div[@class="LocationInfo-address"]//span[@class="c-address-city"]/text()', base.get_first)
#             i.add_xpath('street_address', '//div[@class="LocationInfo-address"]//span[@class="c-address-street-1"]/text()', base.get_first)
#             i.add_xpath('state', '//div[@class="LocationInfo-address"]//abbr[@class="c-address-state"]/text()', base.get_first)
#             i.add_xpath('zip', '//div[@class="LocationInfo-address"]//span[@class="c-address-postal-code"]/text()', base.get_first)
#             i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
#             i.add_xpath('store_number', '//a/@href[contains(., "storeId")]', base.get_first, lambda x: x.split('storeId=')[1].split('&')[0])
#             i.add_xpath('hours_of_operation', '//div[@class="LocationInfo-hoursTable"]//tr[@itemprop="openingHours"]/@content', lambda x: '; '.join(x), lambda x: self.normalize_days(x))
#             if lat_lng not in self.crawled:
#                 self.crawled.add(lat_lng)
#                 return i

#     async def _fetch_stores(self, session, urls):
#         results = []
#         for url in urls:
#             res = await self._fetch_store(session, url)
#             if res:
#                 results.append(res)
#         logger.info(results)
#         return results

#     async def _fetch_city(self, session, url):
#         async with session.get(url, timeout=60 * 60) as response:
#             resp = await response.text()
#             sel = html.fromstring(resp)
#             stores_urls = [urljoin(base_url, s) for s in sel.xpath('//a[@class="Teaser-nameLink"]/@href')]
#             stores = await self._fetch_stores(session, stores_urls)
#             return stores

#     async def _fetch_cities(self, session, urls):
#         results = []
#         for url in urls:
#             res = await self._fetch_city(session, url)
#             results.append(res)
#         return flatten(results)

#     async def _fetch_state(self, session, url):
#         async with session.get(url, timeout=60 * 60) as response:
#             resp = await response.text()
#             sel = html.fromstring(resp)
#             cities_urls = []
#             for href in sel.xpath('//a[@class="c-directory-list-content-item-link"]/@href'):
#                 sp = href.split('/')
#                 if len(sp) == 3:
#                     href = sp[0]+'/'+sp[1] + '.html'
#                 cities_urls.append(urljoin(base_url, href))
#             cities = await self._fetch_cities(session, cities_urls)
#             return cities

#     async def _fetch_all_states(self, urls, loop):
#         connector = aiohttp.TCPConnector(limit=100)
#         async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
#             results = await asyncio.gather(
#                     *[self._fetch_state(session, url) for url in urls],
#                     return_exceptions=True
#                 )
#         return flatten(results)

#     def crawl(self):
#         headers = {
#             "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
#         }
#         body = html.fromstring(requests.get(base_url, headers=headers).text)
#         states = []
#         for href in body.xpath('//a[@class="c-directory-list-content-item-link"]/@href'):
#             sp = href.split('/')
#             if len(sp) == 3:
#                 href = sp[0]+'.html'
#             states.append(urljoin(base_url, href))
#         loop = asyncio.get_event_loop()
#         stores = loop.run_until_complete(self._fetch_all_states(states, loop))
#         return stores
#         # logger.info(stores)

# if __name__ == '__main__':
#     s = Scrape()
#     s.run()
