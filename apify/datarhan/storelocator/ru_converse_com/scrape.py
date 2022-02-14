# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://ru.converse.com/api/catalog/vue_storefront_catalog_1/store/_search?from=0&size=1500&sort="
    domain = "ru.converse.com"
    hdr = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    frm = "{}"

    data = session.post(start_url, headers=hdr, data=frm).json()
    for poi in data["hits"]["hits"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://ru.converse.com/converse-inc/map-stores",
            location_name=poi["_source"]["name"],
            street_address=" ".join(poi["_source"]["address"].split()),
            city=poi["_source"]["city"],
            state=poi["_source"]["region"],
            zip_postal=poi["_source"]["postcode"],
            country_code="RU",
            store_number=poi["_id"],
            phone=poi["_source"]["phone"],
            location_type=poi["_type"],
            latitude=poi["_source"]["latitude"],
            longitude=poi["_source"]["longitude"],
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
