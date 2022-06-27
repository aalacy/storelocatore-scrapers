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

    start_url = "https://www.xpo.com/global-locations/"
    domain = "xpo.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = (
        str(etree.tostring(dom.xpath("//google-maps")[0]))
        .split(':locations-data="')[1]
        .split('" :map-config')[0]
    )

    all_locations = json.loads(data.replace("&quot;", '"').replace("\\", ""))
    for poi in all_locations:
        street_address = poi["street"]
        if poi["address_line_2"]:
            street_address += ", " + poi["address_line_2"]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["office_name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number="",
            phone=poi["telephone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
