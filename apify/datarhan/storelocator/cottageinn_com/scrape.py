import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "cottageinn.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=200&location={}&limit=50&api_key=7b9f27eb343c2baa575fefc41d856ae9&v=20181201&resolvePlaceholders=true"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations = data["response"]["entities"]
        for poi in all_locations:
            if not poi.get("address"):
                continue
            store_url = poi.get("landingPageUrl")
            if not store_url:
                store_url = poi.get("websiteUrl", {}).get("url")
            location_name = poi["name"]
            street_address = poi["address"]["line1"]
            city = poi["address"]["city"]
            state = poi["address"]["region"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["countryCode"]
            store_number = poi["meta"]["id"]
            phone = poi.get("mainPhone")
            location_type = poi["meta"]["entityType"]
            latitude = poi["geocodedCoordinate"]["latitude"]
            longitude = poi["geocodedCoordinate"]["longitude"]
            hours_of_operation = []
            if poi.get("hours"):
                for day, hours in poi["hours"].items():
                    if "holiday" in day:
                        continue
                    if type(hours) == str:
                        continue
                    if hours.get("openIntervals"):
                        opens = hours["openIntervals"][0]["start"]
                        closes = hours["openIntervals"][0]["end"]
                        hours_of_operation.append(f"{day} {opens} - {closes}")
                    else:
                        hours_of_operation.append(f"{day} closed")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )
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
