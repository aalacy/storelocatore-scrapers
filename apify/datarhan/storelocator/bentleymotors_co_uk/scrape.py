from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bentleymotors.co.uk"
    start_url = "https://www.bentleymotors.com/content/brandmaster/global/bentleymotors/en/apps/dealer-locator/jcr:content.api.6cac2a5a11b46ea2d9c31ae3f98bfeb0.json"

    data = session.get(start_url).json()
    for poi in data["dealers"]:
        data = session.get(urljoin(start_url, poi["url"])).json()
        location_name = data["dealerName"]
        street_address = data["addresses"][0]["street"]
        city = data["addresses"][0]["city"]
        zip_code = data["addresses"][0].get("postcode")
        country_code = data["addresses"][0]["country"]
        store_number = data["id"]
        phone = data["addresses"][0]["departments"][0].get("phone")
        phone = phone.split("/")[0] if phone else ""
        latitude = data["addresses"][0]["wgs84"]["lat"]
        longitude = data["addresses"][0]["wgs84"]["lng"]
        hoo = []
        for elem in data["addresses"][0]["departments"][0]["openingHours"]:
            if elem["periods"]:
                day = elem["day"]
                if elem["closed"] is False:
                    opens = elem["periods"][0]["open"]
                    closes = elem["periods"][0]["close"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")

        hours_of_operation = ", ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.bentleymotors.com/en/apps/dealer-locator.html/",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=", ".join(poi["coordinates"][0]["types"]),
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
