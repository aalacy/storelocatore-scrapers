import json

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ccbg.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=200&location={}&limit=25&api_key=2d5a708a656b2665da2abeba0586c932&v=20181201&resolvePlaceholders=true&entityTypes=Location&savedFilterIds=20440614"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations = data["response"]["entities"]

        for poi in all_locations:
            store_url = poi["landingPageUrl"]
            location_name = poi["name"]
            street_address = poi["address"]["line1"]
            city = poi["address"]["city"]
            state = poi["address"]["region"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["countryCode"]
            store_number = poi["meta"]["id"]
            phone = poi.get("mainPhone")
            location_type = ""
            if poi.get("services"):
                location_type = ", ".join(poi["services"])
            latitude = poi["geocodedCoordinate"]["latitude"]
            longitude = poi["geocodedCoordinate"]["longitude"]
            hours_of_operation = []
            if poi.get("hours"):
                for day, hours in poi["hours"].items():
                    if type(hours) == list:
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
