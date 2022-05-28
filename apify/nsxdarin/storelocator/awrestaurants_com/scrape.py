# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://awrestaurants.com/modules/multilocation/?near_location=90210&threshold=40000&distance_unit=miles&limit=5000&services__in=&language_code=en-us&published=1&within_business=true"
    domain = "awrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["objects"]:
        hoo = []
        for e in poi["formatted_hours"]["primary"]["grouped_days"]:
            hoo.append(f'{e["label"]}: {e["content"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["location_url"],
            location_name=poi["location_name"],
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state_name"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["business_id"],
            phone=poi["phones"][0]["number"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lon"],
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
