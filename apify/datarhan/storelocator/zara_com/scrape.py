from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data():
    domain = "zara.com"
    session = SgRequests()
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        url = "https://www.zara.com/{}/en/stores-locator/search?lat={}&lng={}&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true".format(
            all_coords.current_country(), lat, lng
        )
        all_locations = session.get(url, headers=hdr).json()
        if not all_locations:
            all_coords.found_nothing()
        for poi in all_locations:
            street_address = poi["addressLines"][0]
            location_name = poi.get("name")
            if not location_name:
                location_name = street_address
            state = poi.get("state")
            if state == "--":
                state = ""
            if state and state.isdigit():
                state = ""
            zip_code = poi["zipCode"]
            if zip_code and str(zip_code.strip()) == "0":
                zip_code = ""
            phone = poi["phones"]
            phone = phone[0] if phone else ""
            if phone == "--":
                phone = ""

            all_coords.found_location_at(poi["latitude"], poi["longitude"])

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.zara.com/us/en/z-stores-st1404.html?v1=11108",
                location_name=location_name,
                street_address=street_address,
                city=poi["city"],
                state=state,
                zip_postal=zip_code,
                country_code=poi["countryCode"],
                store_number=poi["id"],
                phone=phone,
                location_type=poi["datatype"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation="",
            )
            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
