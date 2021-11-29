import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    domain = "lamborghini.com"
    start_url = "https://www.lamborghini.com/dealers/get.json/en"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["item"]:
        street_address = poi["address"].get("address")
        if not street_address:
            continue
        addr = parse_address_intl(street_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = poi["address"].get("city")
        city = city.split(",")[0] if city else "<MISSING>"
        state = SgRecord.MISSING
        zip_code = poi["address"].get("zip")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        if country_code == "US":
            zip_code = zip_code.split()[-1]
            state = poi["address"]["zip"].split()[0]
        store_number = poi["nid"]
        phone = poi.get("contact", {}).get("phone")
        location_type = poi["type"]["label"]
        latitude = poi.get("coordinates", {}).get("latitude")
        longitude = poi.get("coordinates", {}).get("longitude")
        latitude = latitude.replace(",", ".") if latitude else ""
        longitude = longitude.replace(",", ".") if longitude else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=SgRecord.MISSING,
            location_name=poi["description"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
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
