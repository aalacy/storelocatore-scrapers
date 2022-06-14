# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "leroymerlin.com.br"

    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": "_gaexp=GAX1.3.7NjbEaCAT_eBfsFGr5rW1A.19188.1; GTMUtmTimestamp=1652954052591; GTMUtmSource=(direct); GTMUtmMedium=(none); _gcl_au=1.1.1733969570.1652954053; NoCookie=true; _gid=GA1.3.715796533.1652954054; _tt_enable_cookie=1; _ttp=019fac6d-4a41-4e8d-949a-bb8769394e56; _hjFirstSeen=1; _hjIncludedInSessionSample=1; _hjSession_14486=eyJpZCI6IjIyZDhjMzBmLTY1NWQtNGY4Mi1iNDZhLTc0YTE1YzVlMTRkNiIsImNyZWF0ZWQiOjE2NTI5NTQwNTQ2MzAsImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=0; _fbp=fb.2.1652954054684.760745422; _pin_unauth=dWlkPVl6UXlNR1F4TWpjdE5ERXdaaTAwTTJFMUxXRmtNakV0WldKbVpUUm1ZVFJpWWpjMQ; _clck=u83qvm|1|f1l|0; __cf_bm=Dx3._jueCE9yapEcFPyy5K0Rlj2gyb7M2w3vn.uGd.E-1652954067-0-AeUQAvuytYrbm3VdjcPKE3pTCR5KlxePFn8aXRQXQtXeYPjcQ32oCZ/ooNv+eaMD9v+v4CPqm0DdmoqlypKEvm6NgR3SIW2GnwhgSAfpBMFGP4EfUTeXjADs9IgiX8qX0w==; region=belo_horizonte; user_tracking_id=jv1oxvhmq0wr3iu9r4mty0lqocgbkbqwsrq6aul2; region_name=eyJpdiI6ImV2QlloT0UrVW9wWG5FMU81UXZXOVE9PSIsInZhbHVlIjoiM082dU1HdWFWYzhwWDBTdjhtVVlMZz09IiwibWFjIjoiOWJlNjhiNzE0OGIxOTIyODY3MDNjYzJmZjdjOWFmZDE5NDFmYTYyYzYyNWVlODZjYTA3OTU2NjYxYzg1N2QzYyIsInRhZyI6IiJ9; cache-control-key=9d5d548ac4bc426147abe0dd3e9f251b; _hjSessionUser_14486=eyJpZCI6ImQ2NWMwOGZmLTk0ZDYtNTI3ZC04OTQyLTI1YzFkNjU2N2JlNyIsImNyZWF0ZWQiOjE2NTI5NTQwNTQ1OTIsImV4aXN0aW5nIjp0cnVlfQ==; rr_rcs=eF5jYSlN9ki0SDYyMk1N0TUzTjXQNTGzTNI1SDEx1k1JMjMwNktNM05NMebKLSvJTBEwNDc21zXUNQQAn5IOlA; _dyn_ses.6dd9=*; __gads=ID=619aebe879da6b4b-22b8f351b9d3002c:T=1652954134:S=ALNI_MZO2fQ0rY2zl70ATcmUkyK8Tx2qNw; OptanonAlertBoxClosed=2022-05-19T09:59:06.229Z; _dc_gtm_UA-1162727-2=1; BVBRANDID=8a7ba932-6458-4ada-95f3-8c981b20d6cf; BVBRANDSID=6103eaad-bda1-4ced-9a30-d6c658e4812e; XSRF-TOKEN=eyJpdiI6IllrR3dPVWxmSXkwbDA3dE1qRWFWVVE9PSIsInZhbHVlIjoibzJpaFkrdzU1R1hXRnZBOXhwM29hNWJsTUlCUUdIbU4veGtQMGlXYWpmc1llZXNSaE0zRGtibEswZTd6bnJrTiIsIm1hYyI6ImNiMTgwYzIxNGFhMDAyZDE0ODVmNDE5NmU5MGM4MDM1MzRmYTE1M2ZhNjg2OTBkMzdjYjcwN2ExYWE3NmM0ODMiLCJ0YWciOiIifQ%3D%3D; leroy_session=eyJpdiI6ImlUeGQzVUhXSVZoYU9EYmhXZzR3bkE9PSIsInZhbHVlIjoiU0pyNUtEMHhEb3lNeFFYN0dWWmtSQUZkcWZZNW9HN1FhNkFpdlRzNFhTTzRFaWwyMGNDaTNrQ3A5OWpPTEV2QiIsIm1hYyI6ImZiN2M0YmMyY2IzOGYyYzU4MjRhOGRiMTQ2NzgxOWVjODY4NjYzNzRiNDAwN2I1N2RkOTViN2NiNWEyOTFhMmMiLCJ0YWciOiIifQ%3D%3D; _ga_H3FWJKTQEQ=GS1.1.1652954053.1.1.1652954369.0; _uetsid=a401ad20d75911ecaeac7dfb0cc249f2; _uetvid=a401ff00d75911ec85ca2765ffe6d19c; OptanonConsent=isIABGlobal=false&datestamp=Thu+May+19+2022+11%3A59%3A33+GMT%2B0200+(Central+European+Summer+Time)&version=6.13.0&hosts=&consentId=25c9ce91-2e68-476b-878d-6833ac036a90&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0003%3A1%2CC0002%3A1&geolocation=ES%3BVC&AwaitingReconsent=false; _dyn_id.6dd9=c8a374cd-58f8-5cf0-9e64-57eba035c05d.1652954108.1.1652954373.1652954108.9ffe6792-5d43-496c-9e74-83595e5ba91e; _clsk=u86a9w|1652954374219|4|1|f.clarity.ms/collect; _dd_s=rum=0&expire=1652955280928; _ga=GA1.3.2041587285.1652954054",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    }
    data = session.get(
        "https://www.leroymerlin.com.br/api/boitata/v1/modularContents/53760ebe7269de513c10ddc8/modules?page=1",
        headers=hdr,
    ).json()
    all_regions = data["results"][0]["items"]
    for e in all_regions:
        response = session.get(e["url"], headers=hdr)
        dom = etree.HTML(response.text)
        all_poi = json.loads(dom.xpath("//div/@data-contents")[0])
        for p in all_poi:
            page_url = p["url"]
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//h1[@class="title-1"]/text()')[0]
            raw_address = loc_dom.xpath('//dd[@itemprop="streetAddress"]/text()')[0]
            city = loc_dom.xpath(
                '//ul[@class="m-breadcrumbs"]//span[@itemprop="title"]/text()'
            )[-2].strip()
            if city == "Home":
                addr = parse_address_intl(raw_address)
                city = addr.city
            state = ""
            if len(raw_address.split(" - ")[-1]) == 2:
                state = raw_address.split(" - ")[-1]
            zip_code = loc_dom.xpath('//dd[@itemprop="postalCode"]/text()')[0].replace(
                ".", ""
            )
            phone = loc_dom.xpath('//dd[@itemprop="telephone"]/text()')
            phone = phone[0].split("/")[0].split("(")[0].split("ou")[0] if phone else ""
            geo = (
                loc_dom.xpath('//iframe[@class="map"]/@src')[0]
                .split("ll=")[-1]
                .split("&")[0]
                .replace(",,", ",")
                .split(",")
            )
            if city and "Lojas" in city:
                city = location_name

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address.split(" – ")[0].split(" - ")[0],
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation="",
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
