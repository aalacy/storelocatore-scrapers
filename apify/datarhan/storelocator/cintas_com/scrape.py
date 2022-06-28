# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cintas.com/sitefinity/public/services/locationfinder.svc/search/10001/25000"
    domain = "cintas.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = poi["location"]["Address_1"]
        st_2 = poi["location"]["Address_2"]
        if st_2:
            street_address += ", " + st_2
        zip_code = poi["location"]["Postal"]
        country_code = "USA"
        if len(zip_code.split()) == 2:
            country_code = "CA"
        hoo = "Mon - Fri: 8am - 5pm"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.cintas.com/location-finder/",
            location_name=f"{poi['location']['City']}, {poi['location']['District']}",
            street_address=street_address,
            city=poi["location"]["City"],
            state=poi["location"]["District"],
            zip_postal=zip_code,
            country_code=country_code,
            store_number=poi["location"]["Id"],
            phone=poi["location"]["Services"][0]["Phone"],
            location_type="",
            latitude=poi["location"]["Latitude"],
            longitude=poi["location"]["Longitude"],
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
