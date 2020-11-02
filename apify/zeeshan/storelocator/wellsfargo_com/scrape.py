import re 
import base
import urllib.request, urllib.parse, urllib.error
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class WellsFargo(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'wellsfargo.com'
    url = 'https://www.wellsfargo.com/locator'
    seen = set()

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('branchName')
            ,'street_address': row.get('locationLine1Address')
            ,'city': row.get('city')
            ,'state': row.get('state')
            ,'zip': row.get('postalcode')
            ,'country_code': self.default_country
            ,'store_number': row.get('branchCode')
            ,'phone': row.get('phone')
            ,'location_type': row.get('locationType')
            ,'naics_code': None
            ,'latitude': row.get('latitude')
            ,'longitude': row.get('longitude')
            ,'hours_of_operation': ', '.join(row.get('arrDailyEvents', []))
        }

    def crawl(self):

        session = requests.Session()
        session.headers.update({
            'Accept': '*/*'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.wellsfargo.com'
            ,'Referer': self.url
            ,'X-Requested-With': 'XMLHttpRequest'
        })

        for code, state in self.us_states_with_codes.items():

            cities_request = session.get('https://www.wellsfargo.com/locator/as/getCities/%s' % code.lower())
            if cities_request.status_code == 200:
                cities = re.findall(r'"allCities":(.+),"popularCities":', cities_request.text)
                if cities:
                    cities = eval(cities[0])
                    for city in cities:
                        search_query = '%s, %s' % (city, state)
                        query_params = {
                            'searchTxt': urllib.parse.quote_plus(search_query)
                            ,'mlflg': 'N'
                            ,'sgindex': '99'
                            ,'chflg': 'Y'
                            ,'_bo': 'on'
                            ,'_wl': 'on'
                            ,'_os': 'on'
                            ,'_bdu': 'on'
                            ,'_adu': 'on'
                            ,'_ah': 'on'
                            ,'_sdb': 'on'
                            ,'_aa': 'on'
                            ,'_nt': 'on'
                            ,'_fe': 'on'
                        }

                        del session.headers['X-Requested-With']
                        session.headers.update({
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
                            ,'Accept-Encoding': 'gzip, deflate, br'
                            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
                            ,'Connection': 'keep-alive'
                            ,'Host': 'www.wellsfargo.com'
                            ,'Referer': 'https://www.wellsfargo.com/locator/'
                            ,'Upgrade-Insecure-Requests': '1'
                            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                            ,'Referer': 'https://www.wellsfargo.com/locator/search/?searchTxt=Ardsley%2C+ny&mlflg=N&sgindex=99&chflg=Y&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on'
                        })

                        search_request = session.get('https://www.wellsfargo.com/locator/search/', params=query_params)

                        session.headers.update({
                            'Accept': 'application/json, text/javascript, */*; q=0.01'
                            ,'Content-Type': 'application/json; charset=UTF-8'
                            ,'X-Requested-With': 'XMLHttpRequest'
                        })

                        data_request = session.post('https://www.wellsfargo.com/locator/as/getpayload')

                        data = data_request.json().get('searchResults', [])

                        for row in data:

                            store_number = row.get('branchCode')
                            if store_number in self.seen: continue
                            else: self.seen.add(store_number)

                            yield row


if __name__ == '__main__':
    wf = WellsFargo()
    wf.run()
