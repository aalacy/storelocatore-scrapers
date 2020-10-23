import re
from pprint import pprint
from string import capwords

import base
import sgrequests
from lxml import html, etree
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('amctheatres_com')


crawled = []
class Scrape(base.Spider):
    def crawl(self):
        base_url = "https://www.amctheatres.com/sitemaps/sitemap-theatres.xml"
        session = sgrequests.SgRequests()
        c = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).content
        tree = etree.fromstring(c)
        for href in tree.xpath('//x:urlset/x:url', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            i = base.Item(href.xpath('./y:PageMap',namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"})[0])
            i.add_value('page_url', href.xpath('./x:loc/text()', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}), base.get_first)
            i.add_value('locator_domain', 'https://www.amctheatres.com/movie-theatres')
            i.add_value('location_type', href.xpath('.//y:Attribute[@name="type"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('location_name', href.xpath('.//y:Attribute[@name="title"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('store_number', href.xpath('.//y:Attribute[@name="theatreId"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('street_address', href.xpath('.//y:Attribute[@name="addressLine1"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('city', href.xpath('.//y:Attribute[@name="city"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('state', href.xpath('.//y:Attribute[@name="state"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('zip', href.xpath('.//y:Attribute[@name="postalCode"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('latitude', href.xpath('.//y:Attribute[@name="latitude"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('longitude', href.xpath('.//y:Attribute[@name="longitude"]/text()', namespaces={"y":"http://www.google.com/schemas/sitemap-pagemap/1.0"}), base.get_first)
            i.add_value('country_code', i.as_dict()['state'], lambda x: base.get_country_by_code(x))
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
