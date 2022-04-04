# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=compass-coffee.myshopify.com&latitude=38.9156487&longitude=-77.0737149&max_distance=0&limit=100&calc_distance=1"
    domain = "compasscoffee.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["stores"]:
        if "COMING SOON" in poi["name"]:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://compass-coffee.myshopify.com/apps/store-locator",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["prov_state"],
            zip_postal=poi["postal_zip"],
            country_code=poi["country"],
            store_number=poi["store_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=poi["hours"],
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
