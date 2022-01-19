# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.closeby.co/embed/64c23f7b977dd9b99cda65bef647679e/locations?cachable=true"
    domain = "closeby.co"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["locations"]:
        poi_url = f"https://www.closeby.co/locations/{poi['id']}"
        poi_data = session.get(poi_url).json()
        hoo = []
        for e in poi_data["location"]["location_hours"]:
            day = e["day_full_name"]
            opens = e["time_open"]
            closes = e["time_close"]
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        raw_address = poi_data["location"]["address_full"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += ", " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        if not street_address:
            street_address = raw_address.split(", ")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://mrsimms.co/pages/store-locator",
            location_name=poi["title"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number=poi["id"],
            phone=poi["phone_number"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
