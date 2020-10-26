import re
import time
from string import capwords

import usaddress
from lxml import etree
import base
import requests, json
from urllib.parse import urljoin
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('webster_edu')




class Scrape(base.Spider):
    def crawl(self):
        crawled = []
        base_url = "http://www.webster.edu/locations/"
        # logger.info(requests.get('http://www.webster.edu/locations/index.xml').content)
        for result in etree.fromstring(requests.get('http://www.webster.edu/locations/index.xml').content).xpath('//x:Folder/x:Placemark/x:Placemark/x:Placemark', namespaces={"x":"http://www.opengis.net/kml/2.2"}):
            loc = result.xpath('.//x:description', namespaces={"x": "http://www.opengis.net/kml/2.2"})[0].text.strip().replace('<br/>', ', ').replace(' ,', ',').replace(',,', ',').replace('\xa0', ' ')
            loc_sp = loc.split(',')

            state_zip = usaddress.parse(loc_sp[-2])
            if state_zip:
                if "StateName" in state_zip[0]:
                    i = base.Item(result)
                    url = result.xpath('.//x:ExtendedData/x:Data/x:value', namespaces={"x":"http://www.opengis.net/kml/2.2"})
                    # logger.info([u.text for u in url])
                    # logger.info(url[1])
                    i.add_value('locator_domain', urljoin(base_url, url[1].text))
                    coords = result.xpath('.//x:Point/x:coordinates', namespaces={"x":"http://www.opengis.net/kml/2.2"})[0].text.split(',')
                    i.add_value('location_name', result.xpath('./x:name', namespaces={"x":"http://www.opengis.net/kml/2.2"})[0].text)
                    i.add_value('latitude', coords[1])
                    i.add_value('longitude', coords[0])
                    i.add_value('phone', loc_sp[-1].replace('Phone:', ''), lambda x: x.strip())
                    i.add_value('state', ''.join([s[0] for s in state_zip if s[1] == "StateName"]), lambda x: capwords(x) if len(x) > 2 else x)
                    i.add_value('zip', ''.join([s[0] for s in state_zip if s[1] == "ZipCode"]))
                    i.add_value('city', loc_sp[-3].strip())
                    i.add_value('country_code', 'US')
                    i.add_value('street_address', ', '.join([s.strip() for s in loc_sp][:-3]))
                    if i.as_dict() not in crawled:
                        crawled.append(i.as_dict())
                        yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
