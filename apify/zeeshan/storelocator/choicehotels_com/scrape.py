import base 
import datetime
import requests
import os

import json
import six
from six.moves.urllib import request, parse
import ssl

from pdb import set_trace as bp
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('choicehotels_com')



class ChoiceHotels(base.Base):

    proxy_password = os.environ["PROXY_PASSWORD"]
    proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
    proxy_settings = {
        "http": proxy_url,
        "https": proxy_url
    }

    csv_filename = 'data.csv'
    domain_name = 'choicehotels.com'
    url = 'https://www.choicehotels.com/webapi/location/hotels'

    def _map_data(self, row):
        address = row.get('address', {})
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name')
            ,'street_address': address.get('line1')
            ,'city': address.get('city')
            ,'state': address.get('subdivision')
            ,'zip': address.get('postalCode') 
            ,'country_code': address.get('country')
            ,'store_number': row.get('id')
            ,'phone': row.get('phone') 
            ,'location_type': row.get('brandCode')
            ,'naics_code': None 
            ,'latitude': row.get('lat')
            ,'longitude': row.get('lon')
            ,'hours_of_operation': None
        }

    def do_request(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {
            'adults': 1
            ,'checkInDate': today
            ,'checkOutDate': tomorrow
            ,'hotelSortOrder': 'RELEVANCE'
            ,'include': 'amenity_groups, amenity_totals, rating, relative_media'
            ,'lat': ''
            ,'lon': ''
            ,'minors': 0
            ,'optimizeResponse': 'image_url'
            ,'placeId': ''
            ,'placeName': 'new york'
            ,'placeType': ''
            ,'platformType': 'MOBILE'
            ,'preferredLocaleCode': 'en-us'
            ,'ratePlanCode': 'RACK'
            ,'ratePlans': 'RACK,PREPD,PROMO,FENCD'
            ,'rateType': 'LOW_ALL'
            ,'searchRadius': 100
            ,'siteOpRelevanceSortMethod': 'ALGORITHM_B'
        }
        
        proxy_handler = request.ProxyHandler({
            'http': self.proxy_url,
            'https': self.proxy_url,
        })

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        httpHandler = request.HTTPSHandler(context=ctx)

        opener = request.build_opener(httpHandler,proxy_handler)
        opener.addheaders = self.headers.items()
        return opener.open(self.url, data=parse.urlencode(payload).encode()).read()

    def crawl(self):
        logger.info("in crawl")
        self.headers.update({
            'authority': 'www.choicehotels.com'
            ,'method': 'POST'
            ,'path': '/webapi/location/hotels'
            ,'scheme': 'https'
            ,'accept': 'application/json, text/plain, */*'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'adrum': 'isAjax:true'
            ,'content-type': 'application/x-www-form-urlencoded'
            ,'origin': 'https://www.choicehotels.com'
            ,'referer': 'https://www.choicehotels.com/'
        })
        
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        payload = {
            'adults': 1
            ,'checkInDate': today
            ,'checkOutDate': tomorrow
            ,'hotelSortOrder': 'RELEVANCE'
            ,'include': 'amenity_groups, amenity_totals, rating, relative_media'
            ,'lat': ''
            ,'lon': ''
            ,'minors': 0
            ,'optimizeResponse': 'image_url'
            ,'placeId': ''
            ,'placeName': 'new york'
            ,'placeType': ''
            ,'platformType': 'MOBILE'
            ,'preferredLocaleCode': 'en-us'
            ,'ratePlanCode': 'RACK'
            ,'ratePlans': 'RACK,PREPD,PROMO,FENCD'
            ,'rateType': 'LOW_ALL'
            ,'searchRadius': 100
            ,'siteOpRelevanceSortMethod': 'ALGORITHM_B'
        }
        
        for state in self.us_states:
            payload['placeName'] = state
            logger.info(self.do_request())
            #request = requests.post(self.url, data=payload, headers=self.headers, proxies=self.proxy_settings)
            #logger.info("request status code: {}".format(request.status_code))
            #if request.status_code == 200:
            #    logger.info("got a 200")
            #    obj = request.json()
            #    for hotel in obj.get('hotels', []):
            #        row = self._map_data(hotel)
            #        yield row
            

if __name__ == '__main__':
    logger.info("running choicehotels.py")
    ch = ChoiceHotels()
    ch.run()
