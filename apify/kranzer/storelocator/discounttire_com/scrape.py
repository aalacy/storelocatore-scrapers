import asyncio
import re
from pprint import pprint
from string import capwords

import aiohttp
import base
import lxml.html
import sgrequests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, allow_redirects=False,timeout=60 * 60, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}) as response:
            resp = await response.text()
            if resp:
                sel = lxml.html.fromstring(resp)
                i = base.Item(sel)
                i.add_value('locator_domain', 'https://www.discounttire.com/store-locator')
                i.add_value('page_url', url)
                i.add_value('store_number', url.split('/')[-1])
                addr = sel.xpath('//div[contains(@class, "store-quick-view__address")]/text()')
                if addr:
                    _ = [capwords(s) for s in addr[0].split(', ')]
                    i.add_value('street_address', _[0])
                    counter = 1
                    if base.get_state_code(_[counter]) == "<MISSING>":
                        counter+=1
                    i.add_value('state', base.get_state_code(_[counter]))

                    i.add_value('country_code', i.as_dict()['state'], base.get_country_by_code)
                    i.add_value('city', _[counter+1])
                    i.add_value('zip', _[counter+2])
                js = json.loads(sel.xpath('//script[@type="application/ld+json"][contains(text(), "openingHours")]/text()')[0])
                i.add_value('location_name', js['name'])
                i.add_value('phone', js['telephone'])
                i.add_value('hours_of_operation', '; '.join(js['openingHours']))
                try:
                    lat_lng = sel.xpath('//div[contains(@class, "main-content")]/script[contains(text(), "__pageModel")]/text()')[0]
                    latitude = re.findall(r'store:.+?latitude\":(.+?),', lat_lng)
                    longitude = re.findall(r'store:.+?longitude\":(.+?)\}', lat_lng)
                    i.add_value('latitude', latitude[0])
                    i.add_value('longitude', longitude[0])
                except:
                    pass
                if i.as_dict()['store_number'] not in crawled:
                    crawled.add(i.as_dict()['store_number'])
                    print(i)
                    return i

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results

    def crawl(self):
        base_url = "https://www.discounttire.com/sitemap.xml"
        session = sgrequests.SgRequests()
        response = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
                                                  'x-requested-with': 'XMLHttpRequest',
                                                  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                                  'cookie':"_gcl_au=1.1.299182538.1578436710; _fbp=fb.1.1578436710625.1997362845; __qca=P0-750154980-1578436710358; WRUID=2594673632363036; LPVID=IxNWFmMzI0NzEwOWQxYjk4; _cs_c=1; _ga=GA1.2.202856997.1578436702; __pr.NaN=2yv4dc22to; CTGAIntegration=2594673632363036|202856997.1578436702; storeSetByUser=true; myStoreCookie=1705; JSESSIONID=Y55-31ec2f46-cd8a-496f-9ef1-d19e0e8cdeeb; TS01f46ee3=0106ea43fc307f4cd47f5f3da8e88ce416602605dc2acd0e7cf93a50dbac210d12bd64f3887cef844741f4e7fff05775a4f44e8242f4219d6d40845f192218e5a0caca9b54; rxVisitor=1581773869175BP28SKC4C88U0Q38QCHCU9K3JFIJM0TQ; dtSa=-; dtLatC=115; discounttire-cart=a1ce790d-9743-4e38-aa87-569e67c24661; utag_main=v_id:016f8228cb2500142d33ea97e7d703078002a0700093c$_sn:4$_ss:1$_st:1581775671442$vapi_domain:discounttire.com$_pn:1%3Bexp-session$ses_id:1581773871442%3Bexp-session; check=true; _gid=GA1.2.1045449069.1581773872; mbox=PC#def713e3ac35473b8b19fad906047535.17_0#1645018673|session#041bc04216b74d0da59b6680bfb20c84#1581775733; ctm={'pgv':8441015775013080|'vst':6990110939732889|'vstr':97445495993492|'intr':1581773872780|'v':1|'lvst':47076}; _CT_RS_=Recording; __CT_Data=gpv=9&ckp=tld&dm=discounttire.com&apv_88_www34=9&cpv_88_www34=9&rpv_88_www34=8; dtPC=6$173869166_179h-vBMIFOGCTHSGKDJGJMJKJSAQBFEGDBDKO-0; dtCookie=6$0904911C1C7E4831EFEBB6A0237692E9|080dcdde7f5654da|1; AWSELB=57C379DB040AACF4D1FB5A46E779A6624ACD2543A71FB77E20293E04E1B02CEA6F6E60717A99DE78EC96C5625990E77A386995884A2735A98D5AB4936FA20B821974C6CD266EC71BE4579B2EFCF31450AE208EA05D; rxvt=1581775676699|1581773869179; TS01cd60d2=0106ea43fca823cd92199801bc548d23a2012f1429b869d53f8521c3fde917da97700ec9819bc2fedfc6f3d2202be4122eb895e152ed1b75fe1e5b614fae1a0ee70d37b388eb9b1a1e718636366ff2b6440058084a9427ed9fec37e253ea7129826eb18e49"})
        sitemap = response.content
        url = [s for s in etree.fromstring(sitemap).xpath('//x:sitemap/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"})
               ][1].text
        response = session.get(url, headers={
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
            'x-requested-with': 'XMLHttpRequest',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': "_gcl_au=1.1.299182538.1578436710; _fbp=fb.1.1578436710625.1997362845; __qca=P0-750154980-1578436710358; WRUID=2594673632363036; LPVID=IxNWFmMzI0NzEwOWQxYjk4; _cs_c=1; _ga=GA1.2.202856997.1578436702; __pr.NaN=2yv4dc22to; CTGAIntegration=2594673632363036|202856997.1578436702; storeSetByUser=true; myStoreCookie=1705; JSESSIONID=Y55-31ec2f46-cd8a-496f-9ef1-d19e0e8cdeeb; TS01f46ee3=0106ea43fc307f4cd47f5f3da8e88ce416602605dc2acd0e7cf93a50dbac210d12bd64f3887cef844741f4e7fff05775a4f44e8242f4219d6d40845f192218e5a0caca9b54; rxVisitor=1581773869175BP28SKC4C88U0Q38QCHCU9K3JFIJM0TQ; dtSa=-; dtLatC=115; discounttire-cart=a1ce790d-9743-4e38-aa87-569e67c24661; utag_main=v_id:016f8228cb2500142d33ea97e7d703078002a0700093c$_sn:4$_ss:1$_st:1581775671442$vapi_domain:discounttire.com$_pn:1%3Bexp-session$ses_id:1581773871442%3Bexp-session; check=true; _gid=GA1.2.1045449069.1581773872; mbox=PC#def713e3ac35473b8b19fad906047535.17_0#1645018673|session#041bc04216b74d0da59b6680bfb20c84#1581775733; ctm={'pgv':8441015775013080|'vst':6990110939732889|'vstr':97445495993492|'intr':1581773872780|'v':1|'lvst':47076}; _CT_RS_=Recording; __CT_Data=gpv=9&ckp=tld&dm=discounttire.com&apv_88_www34=9&cpv_88_www34=9&rpv_88_www34=8; dtPC=6$173869166_179h-vBMIFOGCTHSGKDJGJMJKJSAQBFEGDBDKO-0; dtCookie=6$0904911C1C7E4831EFEBB6A0237692E9|080dcdde7f5654da|1; AWSELB=57C379DB040AACF4D1FB5A46E779A6624ACD2543A71FB77E20293E04E1B02CEA6F6E60717A99DE78EC96C5625990E77A386995884A2735A98D5AB4936FA20B821974C6CD266EC71BE4579B2EFCF31450AE208EA05D; rxvt=1581775676699|1581773869179; TS01cd60d2=0106ea43fca823cd92199801bc548d23a2012f1429b869d53f8521c3fde917da97700ec9819bc2fedfc6f3d2202be4122eb895e152ed1b75fe1e5b614fae1a0ee70d37b388eb9b1a1e718636366ff2b6440058084a9427ed9fec37e253ea7129826eb18e49"
        })

        sitemap = response.content
        urls = []
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if "store/" in url:
                urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
