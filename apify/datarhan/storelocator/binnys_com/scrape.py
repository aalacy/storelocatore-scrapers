import re
import demjson
from urllib.parse import urljoin
from w3lib.html import remove_tags

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "binnys.com"
    start_url = "https://www.binnys.com/store-locator"

    response = session.post(start_url)
    data = re.findall("serverSideModel =(.+);", response.text)
    data = demjson.decode(data[0])

    for poi in data["storesGroupedByState"][0]:
        store_url = urljoin(start_url, poi["storePageUrl"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine1"]
        if poi["addressLine2"]:
            street_address += " " + street_address
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zipCode"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = (
            remove_tags(poi["storeHours"])
            .replace("\n", " ")
            .replace("  ", " ")
            .split("&nbsp;")[0]
            .strip()
        )

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
