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

    start_url = "https://www.westelm.com.mx/getstoredetails"
    domain = "westelm.com.mx"

    page_url = "https://www.westelm.com.mx/tienda/browse/storelocator"
    response = session.get(page_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)
    all_locations = data["props"]["pageProps"]["data"]["StoreDataContent"]["stores"]
    for poi in all_locations:
        store_number = poi["storeId"]
        hdr = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "authorization": "[object Object]",
            "brand": "LP",
            "channel": "WEB",
            "content-type": "application/json",
            "customerid": "",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "user-correlation-id": "WLM-WEB-be509962-b2c4-4bd0-8ed3-4ad8a494e8f8",
            "x-correlation-id": "WLM-WEB-be509962-b2c4-4bd0-8ed3-4ad8a494e8f8",
        }
        frm = {"storeId": store_number}
        poi_data = session.post(start_url, headers=hdr, json=frm).json()
        street_address = poi_data["storeDetails"]["StoreDetails"]["1"]["address1"]
        street_address_2 = poi_data["storeDetails"]["StoreDetails"]["1"]["address2"]
        if street_address_2:
            street_address += " " + street_address_2
        poi_html = etree.HTML(
            poi_data["storeDetails"]["StoreDetails"]["1"]["generalDetails"]
        )
        raw_data = poi_html.xpath("//text()")
        hoo = [e.replace("Horario:", "").strip() for e in raw_data if "Horario" in e]
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi_data["storeDetails"]["StoreDetails"]["1"]["state"],
            zip_postal=poi["postalCode"],
            country_code=poi_data["storeDetails"]["StoreDetails"]["1"]["country"],
            store_number=store_number,
            phone=poi_data["storeDetails"]["StoreDetails"]["1"]["phone"],
            location_type=poi["storeType"],
            latitude=poi["lpLatitude"],
            longitude=poi["lpLongitude"],
            hours_of_operation=hoo,
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
