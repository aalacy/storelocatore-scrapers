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

    start_url = "https://shop.rossmann.hu/uzletkereso/"
    domain = "rossmann.hu"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    geo_data = (
        dom.xpath('//script[contains(text(), "initMap")]/text()')[0]
        .split("locations =")[-1]
        .split("var additionals")[0]
        .strip()[:-1]
    )
    geo_data = json.loads(geo_data)
    data = (
        dom.xpath('//script[contains(text(), "initMap")]/text()')[0]
        .split("additionals =")[-1]
        .split("var additionalsCities")[0]
        .strip()[:-1]
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        hoo = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            hoo.append(f"{day} {poi[day]}")
        hoo = " ".join(hoo)
        for e in geo_data:
            if e["id"] == poi["id"]:
                latitude = e["lat"]
                longitude = e["lng"]
                break

        item = SgRecord(
            locator_domain=domain,
            page_url="https://shop.rossmann.hu/uzletkereso/",
            location_name="",
            street_address=poi["street"],
            city=poi["city"],
            state="",
            zip_postal=poi["zip"],
            country_code="",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
