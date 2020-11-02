import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('picknsave_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.picknsave.com/storelocator-sitemap.xml"
        response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        logger.info(response.status_code)
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            logger.info(url)
            if "details" in url:
                div_, store = url.split('details/')[1].split('/')
                data = {
                    "query": "        query storeById($divisionNumber: String!, $storeNumber: String!) {          storeById(divisionNumber: $divisionNumber, storeNumber: $storeNumber) {            banner            bannerDisplayName            divisionNumber            storeNumber            storeType            vanityName            phoneNumber            latitude            longitude            showShopThisStoreAndPreferredStoreButtons            address {              addressLine1              city              stateCode              zip            }            pharmacy {              phoneNumber              formattedHours {                displayName                displayHours                isToday                seoName                seoHours              }            }            formattedHours {              displayName              displayHours              isToday              seoName              seoHours            }            departments {              friendlyName              code            }            onlineServices {              name              url            }            fulfillmentMethods {              hasPickup              hasDelivery            }          }        }",
                    "variables": {"divisionNumber": div_, "storeNumber": store}, "operationName": "storeById"
                }
                headers = {
                    "accept": "application/json, text/plain, */*",
                    "accept-encoding": "gzip, deflate, br",
                    "content-type": "application/json;charset=UTF-8",
                    "origin": "https://www.picknsave.com",
                    "referer": url,
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec_req_type": "ajax",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",

                }
                r = requests.post('https://www.picknsave.com/stores/api/graphql', data=json.dumps(data), headers=headers)
                i = base.Item(r)
                info = r.json()
                i.add_value('location_name', info['data']['storeById']['vanityName'])
                i.add_value('locator_domain', 'https://www.picknsave.com/storelocator')
                i.add_value('page_url', url)
                i.add_value('hours_of_operation', '; '.join([s['displayName'] + ' ' + s['displayHours'] for s in info['data']['storeById']['formattedHours']]))
                i.add_value('phone', info['data']['storeById']['phoneNumber'])
                i.add_value('latitude', info['data']['storeById']['latitude'])
                i.add_value('longitude', info['data']['storeById']['longitude'])
                i.add_value('street_address', info['data']['storeById']['address']['addressLine1'])
                i.add_value('city', info['data']['storeById']['address']['city'])
                i.add_value('state', info['data']['storeById']['address']['stateCode'])
                i.add_value('zip', info['data']['storeById']['address']['zip'])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                i.add_value('store_number', info['data']['storeById']['storeNumber'])
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
