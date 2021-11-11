import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kidtokid.com"
    start_url = "https://kidtokid.com/global/gen/model/search?include_classes=sitefile%2Caddress&take=6000&sort_columns=name%20ASC&location_group_ids=2&country=US&class_string=location"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]["models"]:
        store_url = "https://kidtokid.com/location/{}".format(poi["url"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["street_1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        store_number = poi["location_id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["address"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["address"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = (
            poi["c_store-hours"].replace("\n", " ").replace("\t", " ").strip()
        )
        if not hours_of_operation:
            hours_of_operation = (
                poi["hours_of_operation"].replace("\n", " ").replace("\t", " ")
            )
        hours_of_operation = hours_of_operation.split("for high")[0].strip()
        hours_of_operation = (
            hours_of_operation.split("or anytime")[0].strip().split("Buying")[0].strip()
        )
        hours_of_operation = hours_of_operation.split("Face masks")[0].strip()
        if hours_of_operation.endswith(","):
            hours_of_operation = hours_of_operation[:-1]
        if not hours_of_operation:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
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
            hours_of_operation=hours_of_operation,
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
