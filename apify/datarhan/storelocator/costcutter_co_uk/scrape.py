import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "costcutter.co.uk"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=20&location={}&limit=25&api_key=c6803232fc9ac63c541dc43cd8434aca&v=20181201&resolvePlaceholders=true&languages=en_GB&entityTypes=location"

    all_coods = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=10,
    )

    for code in all_coods:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations = data["response"]["entities"]

        for poi in all_locations:
            store_url = poi.get("landingPageUrl")
            location_name = poi["name"]
            street_address = poi["address"]["line1"]
            if poi["address"].get("line2"):
                street_address += " " + poi["address"]["line2"]
            street_address = " ".join(street_address.split())
            city = poi["address"]["city"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["countryCode"]
            store_number = poi["meta"]["id"]
            phone = poi.get("mainPhone")
            if poi.get("geocodedCoordinate"):
                latitude = poi["geocodedCoordinate"]["latitude"]
                longitude = poi["geocodedCoordinate"]["longitude"]
            hoo = []
            if poi.get("hours"):
                for day, hours in poi["hours"].items():
                    if day == "holidayHours":
                        continue
                    if hours.get("openIntervals"):
                        opens = hours["openIntervals"][0]["start"]
                        closes = hours["openIntervals"][0]["end"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
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
