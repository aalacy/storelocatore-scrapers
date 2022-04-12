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

    start_url = "https://www.liverpool.com.mx/tienda/browse/storelocator"
    domain = "liverpool.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)

    all_locations = data["props"]["pageProps"]["data"]["StoreDataContent"]["stores"]
    for poi in all_locations:
        store_number = poi["storeId"]
        frm = {"storeId": store_number}
        post_url = "https://www.liverpool.com.mx/getstoredetails"
        poi_data = session.post(post_url, data=frm, headers=hdr).json()
        street_address = poi_data["storeDetails"]["StoreDetails"]["1"]["address1"]
        if poi_data["storeDetails"]["StoreDetails"]["1"]["address2"]:
            street_address += (
                " " + poi_data["storeDetails"]["StoreDetails"]["1"]["address2"]
            )
        poi_html = etree.HTML(
            poi_data["storeDetails"]["StoreDetails"]["1"]["generalDetails"]
        )
        hoo = [e.strip() for e in poi_html.xpath("//text()") if "Horario" in e][
            0
        ].split("tienda:")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
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
