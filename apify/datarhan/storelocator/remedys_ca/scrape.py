import re
import json
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.remedys.ca/api/sitecore/Pharmacy/Pharmacies?id=%7B0018F0E6-DF33-46DA-B4D8-51C5C8441883%7D"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data["pharmacies"]:
        store_url = urljoin(start_url, poi["detailUrl"])
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        addr = parse_address_intl(poi["address"])
        street_address = poi["address"].split(",")[0]
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeCode"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        latitude = latitude if latitude and len(str(latitude)) > 2 else "<MISSING>"
        longitude = poi["location"]["longitude"]
        longitude = longitude if longitude and len(str(longitude)) > 2 else "<MISSING>"

        hoo = []
        for elem in poi["storeOpeningHours"]:
            day = elem["day"]
            hours = elem["openDuration"]
            hoo.append(f"{day} {hours}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
