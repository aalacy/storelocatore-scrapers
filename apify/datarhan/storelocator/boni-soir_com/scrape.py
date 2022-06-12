# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.boni-soir.com/wp-content/stores/stores.json"
    domain = "boni-soir.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        store_number = poi["ID"]
        poi_data_url = f"https://www.boni-soir.com/wp-json/wp/v2/store/{store_number}"
        poi_data = session.get(poi_data_url, headers=hdr)
        while poi_data.status_code != 200:
            session = SgRequests()
            poi_data = session.get(poi_data_url, headers=hdr)
            print("!!!!", poi)
        poi_data = poi_data.json()
        street_address = poi_data["store_details"]["location_address_address_1"]
        street_address_2 = poi_data["store_details"]["location_address_address_2"]
        if street_address_2:
            street_address += " " + street_address_2
        hoo = []
        for day, hours in poi_data["store_details"]["hours"].items():
            if not hours:
                hours = "closed"
            hoo.append(f"{day}: {hours}")
        hoo = " ".join(hoo)

        phone = ""
        loc_response = session.get(poi_data["link"], headers=hdr)
        if loc_response.status_code == 200:
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//span[@class="phone"]/a/text()')
            phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=poi_data["link"],
            location_name=poi_data["store_details"]["title"]["raw"],
            street_address=street_address,
            city=poi_data["store_details"]["city"],
            state=poi_data["store_details"]["store_region"]["name"],
            zip_postal=poi_data["store_details"]["postal_code"],
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type=poi_data["type"],
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
