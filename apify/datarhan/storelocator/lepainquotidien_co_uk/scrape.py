import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "lepainquotidien.com"
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        start_url = (
            "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location="
            + f"{lat},{lng}"
            + "&radius=200&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false}}"
        )
        response = session.get(start_url)
        data = json.loads(response.text)
        all_locations = data["response"]["entities"]

        for poi in all_locations:
            location_name = poi.get("c_bIReference")
            if not location_name:
                location_name = poi["meta"]["id"].replace("-", " ")
            street_address = poi["address"]["line1"]
            page_url = poi.get("c_facebookWebsiteOverride")
            page_url = (
                page_url.split("?")[0]
                if page_url
                else poi["googleWebsiteOverride"].split("?")[0]
            )
            city = poi["address"]["city"]
            state = poi["address"].get("region")
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["countryCode"]
            if country_code != "GB":
                continue
            phone = poi["mainPhone"]
            location_type = ", ".join(poi["meta"]["schemaTypes"])
            latitude = poi["geocodedCoordinate"]["latitude"]
            longitude = poi["geocodedCoordinate"]["longitude"]
            hoo = []
            for day, hours in poi["hours"].items():
                if day in ["reopenDate", "holidayHours"]:
                    continue
                if hours.get("isClosed"):
                    hoo.append(f"{day} closed")
                else:
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
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
