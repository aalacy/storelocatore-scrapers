# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://adecco.com.mx/sucursales/"
    domain = "adecco.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[@id="sucursales-js-extra"]/text()')[0]
        .split("constants =")[-1]
        .split(";/*")[0]
    )
    data = json.loads(data)

    all_locations = []
    for k, v in data["branches"].items():
        if k.isdigit():
            all_locations.append(v)
        else:
            for l in v.values():
                all_locations.append(l)

    for poi in all_locations:
        phone = poi["phone"].split("/")[0] if poi["phone"] != "0" else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://adecco.com.mx/sucursales/",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="MX",
            store_number=poi["id"],
            phone=phone,
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
