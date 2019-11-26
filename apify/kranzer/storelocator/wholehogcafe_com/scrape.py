import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):
    crawled = set()
    def crawl(self):
        base_url = "https://www.wholehogcafe.com/locations/"
        body = [urljoin(base_url, l) for l in re.findall(r'window.location.href=\"(//www.whole.+?)\"',requests.get(base_url, verify=False).text)]
        for result in body:
            res_sel = base.selector(result, verify=False)
            json_data_url = "https://www.wholehogcafe.com/wp-admin/admin-ajax.php"
            headers = {
                "Accept":"application/json, text/javascript, */*; q=0.01",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
            }
            body = "action=hugeit_maps_get_info&map_id={}".format(res_sel['tree'].xpath('//div/@data-map_id')[0])
            data = {}
            js = requests.post(json_data_url, headers=headers, data=body, verify=False).json()
            markers = js.get('success', {}).get('markers', [])
            for m in markers:
                name = m['description'][:m['description'].find(',')].encode('utf8').replace(b'\xe2\x80\x93', b'-').decode('utf8')
                data[name] = {
                    "id": m['id'],
                    "lat": m['lat'],
                    "lng": m['lng']
                }
            for record in res_sel['tree'].xpath('//tbody//tr[count(td)=3]'):
                texts = [r.replace('\t','').replace('\n', '') for r in record.xpath('./td[1]//text()')]
                texts = [r for r in texts if r]
                if "Address" not in texts:
                    i = base.Item(record)
                    i.add_value('locator_domain', base_url)
                    i.add_value('page_url', res_sel['url'])
                    i.add_value('location_name', texts[0])
                    n = texts[0].encode('utf8').replace(b'\xe2\x80\x93', b'-').decode('utf8')
                    del texts[0]
                    n = n[:int(len(n)*0.65)+1]
                    for k, v in data.items():
                        if n in k:
                            i.add_value('latitude', v.get('lat'))
                            i.add_value('longitude', v.get('lng'))
                            i.add_value('store_number', v.get('id'))
                    loc = texts.pop()
                    if loc:
                        tup = re.findall(r'(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                        if tup:
                            i.add_value('city', tup[0][0])
                            i.add_value('state', tup[0][1])
                            i.add_value('zip', tup[0][2])
                            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    i.add_value('street_address', ' '.join(texts))
                    i.add_xpath('phone', './td[2]/text()', base.get_first, lambda x: x.replace('Phone: ', ''), lambda x: x.replace('\n','').replace('\t',''))
                    i.add_xpath('hours_of_operation', './td[3]/text()', lambda x: [s.replace('\n', '').replace('\t', '').strip() for s in x], lambda x: '; '.join([s for s in x if s]))
                    if i.as_dict()['store_number'] != "<MISSING>":
                        if i.as_dict()['store_number'] not in self.crawled:
                            self.crawled.add(i.as_dict()['store_number'])
                            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
