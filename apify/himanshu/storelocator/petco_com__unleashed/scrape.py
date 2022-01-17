# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://maps.stores.petco.com/api/getAsyncLocations?template=search&level=search&search={}&radius=100"
    domain = "petco.com/unleashed"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        if not data["markers"]:
            continue
        for poi in data["markers"]:
            poi_data = json.loads(etree.HTML(poi["info"]).xpath("//div/text()")[0])
            if poi_data["location_name"] != "Unleashed":
                continue
            page_url = poi_data["url"]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            street_address = poi_data["address_1"]
            if poi_data["address_2"]:
                street_address += ", " + poi_data["address_2"]
            hoo = loc_dom.xpath('//div[@class="hours"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi_data["location_display_name"],
                street_address=street_address,
                city=poi_data["city"],
                state=poi_data["region"],
                zip_postal=poi_data["post_code"],
                country_code="",
                store_number=poi["locationId"],
                phone=poi_data["local_phone"],
                location_type=poi_data["location_name"],
                latitude=poi["lat"],
                longitude=poi["lng"],
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
