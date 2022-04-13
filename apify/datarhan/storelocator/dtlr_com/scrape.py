import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "dtlr.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=200&location=%22{}%22&limit=50&api_key=252cd5124c2d1f935854409f130acc61&v=20181201&resolvePlaceholders=true&entityTypes=location"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=200,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations = data["response"]["entities"]

        for poi in all_locations:
            page_url = poi.get("landingPageUrl")
            location_name = poi["name"]
            street_address = poi["address"]["line1"]
            if poi["address"].get("line2"):
                street_address += ", " + poi["address"]["line2"]
            city = poi["address"]["city"]
            state = poi["address"]["region"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["countryCode"]
            store_number = poi["meta"]["id"]
            phone = poi.get("localPhone")
            location_type = poi["meta"]["entityType"]
            latitude = poi.get("geocodedCoordinate", {}).get("latitude")
            if not latitude:
                latitude = poi.get("yextDisplayCoordinate", {}).get("latitude")
            longitude = poi.get("geocodedCoordinate", {}).get("longitude")
            if not longitude:
                longitude = poi.get("yextDisplayCoordinate", {}).get("longitude")
            hours_of_operation = []
            if poi.get("hours"):
                for day, hours in poi["hours"].items():
                    if day in ["reopenDate", "holidayHours"]:
                        continue
                    if type(hours) == dict and hours.get("isClosed"):
                        hours_of_operation.append(f"{day} closed")
                    else:
                        opens = hours["openIntervals"][0]["start"]
                        closes = hours["openIntervals"][0]["end"]
                        hours_of_operation.append(f"{day} {opens} - {closes}")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
