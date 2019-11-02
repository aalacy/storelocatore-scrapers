import ast
import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):
    crawled = set()
    def crawl(self):

        base_url = "http://claimjumper.com/locations.aspx"
        body = html.fromstring(requests.get(base_url).text)
        js_ = body.xpath('//script/text()[contains(., "location_info_array_string")]')[0]
        js = re.findall(r'location_info_array_string = (\'.+?\');', js_)[0]
        _ = ast.literal_eval('['+js[1:-1].replace('|',',')+']')
        data = {}
        for i in _:
            data[i['name']] = i
        for result in body.xpath('//div[@class="location_container"]'):
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('location_name', './/h1[@id="LocationTitle"]//text()', lambda x: [s for s in x if s.strip()], base.get_first, lambda x: capwords(x))
            i.add_value('latitude', data.get(i.as_dict()['location_name'], {}).get('lat'))
            i.add_value('longitude', data.get(i.as_dict()['location_name'], {}).get('long'))
            i.add_value('store_number', data.get(i.as_dict()['location_name'], {}).get('storenum'))
            loc = result.xpath('.//div[contains(@id,"Address")]/text()')[0]
            if loc:
                tup = re.findall(r'(.+)\s(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                if tup:
                    i.add_value('street_address', tup[0][0])
                    i.add_value('city', tup[0][1])
                    i.add_value('state', tup[0][2])
                    i.add_value('zip', tup[0][3])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('phone', './/span[contains(@id,"Phone")]/text()', base.get_first, lambda x: x[:-1] if i.as_dict()['location_name']=="Tualatin" else x)
            i.add_xpath('hours_of_operation', './/div[contains(@id,"LocationHours")]//text()',
                        lambda x: [s.replace('\n', '').replace('\t', '').strip() for s in x],
                        lambda x: '; '.join([s for s in x if s]),
                        lambda x: x.replace('Hours:;', 'Hours:'))
            if i.as_dict()['store_number'] not in self.crawled:
                self.crawled.add(i.as_dict()['store_number'])
                yield i

        # for result in body:
        #     res_sel = base.selector(result, verify=False)
        #     json_data_url = "https://www.wholehogcafe.com/wp-admin/admin-ajax.php"
        #     headers = {
        #         "Accept":"application/json, text/javascript, */*; q=0.01",
        #         "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
        #     }
        #     body = "action=hugeit_maps_get_info&map_id={}".format(res_sel['tree'].xpath('//div/@data-map_id')[0])
        #     data = {}
        #     js = requests.post(json_data_url, headers=headers, data=body, verify=False).json()
        #     markers = js.get('success', {}).get('markers', [])
        #     for m in markers:
        #         data[m['description'][:m['description'].find(',')]] = {
        #             "id": m['id'],
        #             "lat": m['lat'],
        #             "lng": m['lng']
        #         }
        #     for record in res_sel['tree'].xpath('//tbody//tr[count(td)=3]')[1:]:
        #         texts = [r.replace('\t','').replace('\n', '') for r in record.xpath('./td[1]//text()')]
        #         texts = [r for r in texts if r]
        #         i = base.Item(record)
        #         i.add_value('locator_domain', base_url)
        #         i.add_value('page_url', res_sel['url'])
        #         i.add_value('location_name', texts[0])
        #         del texts[0]
        #         i.add_value('latitude', data.get(i.as_dict()['location_name'], {}).get('lat'))
        #         i.add_value('longitude', data.get(i.as_dict()['location_name'], {}).get('lng'))
        #         i.add_value('store_number', data.get(i.as_dict()['location_name'], {}).get('id'))
        #         loc = texts.pop()
        #         if loc:
        #             tup = re.findall(r'(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
        #             if tup:
        #                 i.add_value('city', tup[0][0])
        #                 i.add_value('state', tup[0][1])
        #                 i.add_value('zip', tup[0][2])
        #                 i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
        #         i.add_value('street_address', ' '.join(texts))
        #         i.add_xpath('phone', './td[2]/text()', base.get_first, lambda x: x.replace('Phone: ', ''))
        #         i.add_xpath('hours_of_operation', './td[3]/text()', lambda x: [s.replace('\n', '').replace('\t', '').strip() for s in x], lambda x: '; '.join([s for s in x if s]))
        #         if i.as_dict()['store_number'] != "<MISSING>":
        #             yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
