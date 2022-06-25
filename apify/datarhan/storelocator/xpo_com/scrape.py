# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import ssl
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cashexpressllc.com/api/v1/get-stores"
    domain = "xpo.com"
    hdr = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": "eyJpdiI6IlQ4d0RoMGlkMkg5M09BVnFFMm9NUlE9PSIsInZhbHVlIjoiVngvNDk0ZVZWWlNJbUlWNjBUT3lZVERFaXZ6S3h5Smw4eGpaNzVXU3UrbUtBanQ5bFBzMisyRjkxTFNxODhRRWg0WnNoVVV5NXg3aGlwb04yMjhlSlI3UGxvSm1JNWQrODRqMExOZDZOR0pQZnVyWFAydVJwVHIvT0ErUnB1TSsiLCJtYWMiOiI0Mzk0Nzc5MWJkMmMzMTc3YzEzMmE0MjJmODkxYTcwNWQ2OWZhNDAyYTFjZjg1N2E4MjBlYWM5ZWE0YzNlMTc3IiwidGFnIjoiIn0=",
    }
    data = session.post(start_url, headers=hdr).json()
    for poi in data["stores"]:
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        mon = f'Monday {poi["mon_open"][:-3]}-{poi["mon_close"][:-3]}'
        tue = f'Tuesday {poi["tue_open"][:-3]}-{poi["tue_close"][:-3]}'
        wed = f'Wednesday {poi["wed_open"][:-3]}-{poi["wed_close"][:-3]}'
        thu = f'Thursday {poi["thu_open"][:-3]}-{poi["thu_close"][:-3]}'
        fri = f'Friday {poi["fri_open"][:-3]}-{poi["fri_close"][:-3]}'
        sat = f'Satarday {poi["sat_open"][:-3]}-{poi["sat_close"][:-3]}'
        sun = f'Sunday {poi["sun_open"][:-3]}-{poi["sun_close"][:-3]}'
        hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.xpo.com/global-locations/",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["store_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
