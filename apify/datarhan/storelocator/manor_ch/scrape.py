# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.manor.ch/de/store-finder"
    domain = "manor.ch"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)

    all_store_numbers = []
    for k in data["props"]["pageProps"]["initialApolloState"].keys():
        if "Store:" in k:
            all_store_numbers.append(k)

    for store_number in all_store_numbers:
        poi = data["props"]["pageProps"]["initialApolloState"][store_number]
        poi_data = data["props"]["pageProps"]["initialApolloState"][
            poi["address"]["__ref"]
        ]
        street_address = poi_data["street"] + " " + poi_data["streetNo"]
        page_url = f'https://www.manor.ch/de/store-finder/store/{poi["siteId"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//div[p[contains(text(), "Shops & Öffnungszeiten")]]/following-sibling::div[1]/div[1]//text()'
        )
        hoo = " ".join(hoo[:2])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi_data["city"],
            state="",
            zip_postal=poi_data["zip"],
            country_code="",
            store_number=poi["id"],
            phone="",
            location_type=poi["__typename"],
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
