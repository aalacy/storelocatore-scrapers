import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()

    domain = "dxl.com"
    start_url = "https://stores.dxl.com/search?q={}&r=200"

    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        expected_search_radius_miles=50,
    )

    for code in all_codes:
        response = session.get(start_url.format(code), headers=headers)
        data = json.loads(response.text)

        for poi in data["response"]["entities"]:
            store_url = "https://stores.dxl.com/" + poi["url"]
            location_name = poi["profile"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["profile"]["address"]["line1"]
            if poi["profile"]["address"]["line2"]:
                street_address += ", " + poi["profile"]["address"]["line2"]
            if poi["profile"]["address"]["line3"]:
                street_address += ", " + poi["profile"]["address"]["line3"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["profile"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["profile"]["address"]["region"]
            state = state if state else "<MISSING>"
            zip_code = poi["profile"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["profile"]["address"]["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["profile"]["mainPhone"]["display"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["profile"]["c_pagesLocatorStoreType"]
            location_type = location_type[0] if location_type else "<MISSING>"
            latitude = ""
            longitude = ""
            if poi["profile"].get("geocodedCoordinate"):
                latitude = poi["profile"]["geocodedCoordinate"]["lat"]
                longitude = poi["profile"]["geocodedCoordinate"]["long"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []

            if poi["profile"].get("hours"):
                for elem in poi["profile"]["hours"]["normalHours"]:
                    day = elem["day"]
                    if elem["intervals"]:
                        opens = str(elem["intervals"][0]["start"])
                        opens = opens[:-2] + ":" + opens[-2:]
                        closes = str(elem["intervals"][0]["end"])
                        closes = closes[:-2] + ":" + closes[-2:]
                        hours_of_operation.append(f"{day} {opens} - {closes}")
                    else:
                        hours_of_operation.append(f"{day} cloased")
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
