import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class DaylightDonuts(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'daylightdonuts.com'
    url = 'http://www.daylightdonuts.com/wp-admin/admin-ajax.php'

    def map_data(self, row):
        times = html.fromstring(row.get('hours')).xpath('//tr//td')
        hours = ', '.join(['%s: %s' % (times[i].text, xpath(times[i+1], './time/text()')) for i in range(len(times)/2) if times[i] is not None and times[i+1] is not None])
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('store', '')
            ,'street_address': row.get('address', '')
            ,'city': row.get('city', '')
            ,'state': row.get('state', '')
            ,'zip': row.get('zip', '')
            ,'country_code': self.default_country
            ,'store_number': row.get('id', '')
            ,'phone': row.get('phone', '')
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': row.get('lat', '')
            ,'longitude': row.get('lng', '')
            ,'hours_of_operation': hours
        }

    def crawl(self):

        session = requests.Session()
        session.headers.update({
            'Accept': '*/*'
            ,'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.daylightdonuts.com'
            ,'Referer': 'http://www.daylightdonuts.com/find-your-daylight/'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        })
        query_params = {
            'action': 'store_search'
            ,'lat': '36.15398'
            ,'lng': '-95.99277'
            ,'max_results': '10000'
            ,'search_radius': '10000'
            ,'autoload': '1'
            ,'_': '1564199818851'
        }

        request = session.get(self.url, params=query_params)
        if request.status_code == 200:
            rows = request.json()
            for row in rows:
                yield row


if __name__ == '__main__':
    dd = DaylightDonuts()
    dd.run()
