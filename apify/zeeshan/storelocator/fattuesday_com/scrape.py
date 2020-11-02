import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class FatTuesday(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'fattuesday.com'
    url = 'https://fattuesday.com/wp-admin/admin-ajax.php'

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name', '<MISSING>')
            ,'street_address': row.get('address', '<MISSING>')
            ,'city': row.get('city', '<MISSING>')
            ,'state': row.get('state', '<MISSING>')
            ,'zip': row.get('zip', '<MISSING>')
            ,'country_code': row.get('country', '<MISSING>')
            ,'store_number': row.get('id', '<MISSING>')
            ,'phone': row.get('phone', '<MISSING>')
            ,'location_type': row.get('tags', '<MISSING>')
            ,'naics_code': None
            ,'latitude': row.get('lat', '<MISSING>')
            ,'longitude': row.get('lng', '<MISSING>')
            ,'hours_of_operation': row.get('hours', '<MISSING>')
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'fattuesday.com'
            ,'method': 'POST'
            ,'path': '/wp-admin/admin-ajax.php'
            ,'scheme': 'https'
            ,'accept': '*/*'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
            ,'origin': 'https://fattuesday.com'
            ,'referer': 'https://fattuesday.com/locations/'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            ,'x-requested-with': 'XMLHttpRequest'
        })
        payload = {
            'address': '' 
            ,'formdata': 'addressInput='
            ,'lat': '37.09024'
            ,'lng': '-95.71289100000001'
            ,'name': ''
            ,'options[distance_unit]': 'miles'
            ,'options[dropdown_style]': 'none'
            ,'options[ignore_radius]': '0'
            ,'options[immediately_show_locations]': '1'
            ,'options[initial_radius]': '10000'
            ,'options[label_directions]': ''
            ,'options[label_email]': '' 
            ,'options[label_fax]': 'Social'
            ,'options[label_phone]': 'Phone'
            ,'options[label_website]': 'Website'
            ,'options[loading_indicator]': ''
            ,'options[map_center]': 'United States'
            ,'options[map_center_lat]': '37.09024'
            ,'options[map_center_lng]': '-95.712891'
            ,'options[map_domain]': 'maps.google.com'
            ,'options[map_end_icon]': 'https://fattuesday.com/wp-content/uploads/2017/02/FunkyFTCup.png'
            ,'options[map_home_icon]': 'https://fattuesday.com/wp-content/plugins/store-locator-le/images/icons/bulb_azureonsilver.png'
            ,'options[map_region]': 'us'
            ,'options[map_type]': 'roadmap'
            ,'options[message_bad_address]': 'Could not locate this address. Please try a different location.'
            ,'options[message_no_results]': 'No locations found.'
            ,'options[no_autozoom]': '0'
            ,'options[use_sensor]': '0'
            ,'options[zoom_level]': '19'
            ,'options[zoom_tweak]': '1'
            ,'options[limit]': '10000'
            ,'radius': '10000'
            ,'limit': '10000'
            ,'tags': ''
            ,'action': 'csl_ajax_onload'
        }
        request = session.post(self.url, data=payload)
        if request.status_code == 200:
            for row in request.json().get('response'):
                yield row


if __name__ == '__main__':
    ft = FatTuesday()
    ft.run()
