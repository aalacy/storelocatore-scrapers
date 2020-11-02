import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://us.caudalie.com/store-locator/ajax?center_latitude=37.09024&center_longitude=-95.71289100000001&south_west_latitude=37.063533557981614&north_east_latitude=37.116937034104765&south_west_longitude=-95.77468909570314&north_east_longitude=-95.65109290429689&current_zoom=14&_=1566120549970"
        body = requests.get(base_url).json()
        for json_resp in body:
            state = ""
            lat = json_resp['latitude']
            flag = False
            for s in [capwords(a) for a in base.us_states] + list(base.us_states_codes) + [capwords(a) for a in base.ca_provinces] + list(base.ca_provinces_codes):
                if (' '+s+' ' in json_resp['address'] or ' '+s+',' in json_resp['address']) and "France" not in json_resp['address'] and "Belgique" not in json_resp['address'] and "Italia" not in json_resp['address'] and "Deutschland" not in json_resp['address']:
                    if float(lat)>0:
                        flag=True
                        state=s
                        break
            if flag:
                i = base.Item(json_resp)
                i.add_value('locator_domain', 'https://us.caudalie.com/store-locator')
                i.add_value('location_name', json_resp['label'])
                i.add_value('store_number', json_resp['id'])
                if "<br>" in json_resp['address']:
                    try:
                        loc = json_resp['address'][json_resp['address'].find('<br>')+4:].split(', '+state)
                        i.add_value('city', loc[0])
                        i.add_value('zip', loc[1], lambda x: x.strip()[:3]+' '+x.strip()[3:] if ' ' not in x.strip() and len(x.strip())==6 else x.strip())
                        i.add_value('street_address', json_resp['address'].split('<br>')[0])
                    except:
                        pass
                else:
                    try:
                        loc = [l for l in json_resp['address'][:json_resp['address'].find(', '+state)].split(',')[-1].split(' ') if l]
                        i.add_value('zip', loc[0], lambda x: x.strip()[:3]+' '+x.strip()[3:] if ' ' not in x.strip() and len(x.strip())==6 else x.strip())
                        i.add_value('city', loc[1])
                        i.add_value('street_address', json_resp['address'].split(', '+loc[0])[0])
                    except:
                        pass

                i.add_value('latitude', lat)
                i.add_value('longitude', json_resp['longitude'])
                i.add_value('state', state)
                i.add_value('country_code', base.get_country_by_code(state.lower()) if len(state) > 2 else base.get_country_by_code(state))
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
