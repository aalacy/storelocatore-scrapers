import re
import requests
import json
from w3lib.html import remove_tags
import base
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gfs_com')



class Scrape(base.Spider):
    data = []
    locator_domain = "https://gfsstore.com/locations/"
    base_url = "https://gfsstore.com/"
    def crawl(self):
        r = requests.get(self.base_url+'stores_jsonp/?callback=jQuery112408348595095024478_1564832094867')
        locations = json.loads(re.findall(r'.+?\((.+)\)', r.text)[0])
        for location in locations:
            type = location['field_location_type'][0]['value'].strip()
            if type == "grm":
                type = "Gordon Restaurant Market"
            elif type == "store":
                type = "Gordon Food Service Stores"
                #logger.info("here")
            else:
                continue
            item = base.Item(location)
            item.add_value('locator_domain', self.locator_domain)
            item.add_value('location_name', location['title'] or "<MISSING>")
            item.add_value('street_address', location['field_address'][0]['thoroughfare'] or "<MISSING>")
            item.add_value('city', location['field_address'][0]['locality'] or "<MISSING>")
            item.add_value('state', location['field_address'][0]['administrative_area'] or "<MISSING>")
            item.add_value('zip', location['field_address'][0]['postal_code'] or "<MISSING>")
            item.add_value('country_code', location['field_address'][0]['country'] or "<MISSING>")
            item.add_value('store_number', location['nid'] or "<MISSING>")
            item.add_value('phone', location['field_phone'][0]['safe_value'] or "<MISSING>")
            item.add_value('location_type', type )
            item.add_value('latitude', location['field_latitude'][0]['value'] or "<MISSING>")
            item.add_value('longitude', location['field_longitude'][0]['value'] or "<MISSING>")
            item.add_value('hours_of_operation', remove_tags(location['field_hours'][0]['safe_value'].replace('<br>', '; ')).strip() or "<MISSING>")
            yield item


if __name__ == '__main__':
    s = Scrape()
    s.run()
