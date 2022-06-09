# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.harmonsgrocery.com/wp/wp-admin/admin-ajax.php?action=get_ajax_posts&nextNonce=f9813ac444"
    domain = "harmonsgrocery.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        raw_data = etree.HTML(poi["address"]).xpath("//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.harmonsgrocery.com/locations",
            location_name=poi["name"],
            street_address=raw_data[0],
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[-1].split()[0],
            zip_postal=raw_data[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number=poi["pharmacy"],
            phone=raw_data[2],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=" ".join(raw_data[3:]),
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
