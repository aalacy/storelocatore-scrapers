import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class FitnessPremierClubs(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'fitnesspremierclubs.com'
    url = 'https://www.fitnesspremierclubs.com'
    seen = set()

    def map_data(self, row):
        street_address, city, state, zipcode = row.get('address1'), row.get('city'), row.get('state'), row.get('zip', '').strip()
        address = '%s, %s, %s %s' % (street_address, city, state, zipcode,)
        geo = self.get_geo(address)
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name', '')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': row.get('country', '')
            ,'store_number': row.get('number', '')
            ,'phone': row.get('phone', '').replace(' Ext.', '')
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': geo.get('lat', '')
            ,'longitude': geo.get('lng', '')
            ,'hours_of_operation': '24/7'
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like ,Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })
        homepage = session.get(self.url)
        if homepage.status_code == 200:
            locations = html.fromstring(homepage.text).xpath('//ul[@class="sub-menu"][1]//li//a//@href')
            for location_url in locations:
                location_page = session.get(location_url)
                if location_page.status_code == 200:
                    club_number = re.findall(r'clubNumber=(\d+)', location_page.text)
                    club_number = club_number[0] if club_number else None
                    if club_number:
                        club_url = 'https://mico.myiclubonline.com/iclub/club/getClubExternal.htm?club=%s&_=1564200271209' % club_number
                        club_request = session.get(club_url, headers= {
                            'Accept': 'application/json, text/javascript, */*; q=0.01'
                            ,'Referer': 'https://mico.myiclubonline.com/iclub/classlist.htm?clubNumber=%s' % club_number
                            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
                            ,'X-Requested-With': 'XMLHttpRequest'
                        })
                        if club_request.status_code == 200:
                            rows = club_request.json()
                            for row in rows:
                                store_number = row.get('number', '')
                                if store_number in self.seen:
                                    continue
                                self.seen.add(store_number)
                                yield row


if __name__ == '__main__':
    fpc = FitnessPremierClubs()
    fpc.run()
