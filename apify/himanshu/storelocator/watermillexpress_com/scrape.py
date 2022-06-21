from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("watermillexpress_com")


session = SgRequests()


def fetch_data():
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=500,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    for lat, lng in coords:

        location_url = "https://watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=500&search_radius=500&search=&statistics="
        all_locations = session.get(
            location_url.format(lat, lng), headers=headers
        ).json()
        if not all_locations:
            coords.found_nothing()

        for poi in all_locations:
            address2 = poi["address2"]
            street_address = poi["address"] + " " + str(address2).replace("None", "")
            hours_of_operation = "Open 24/7"
            coords.found_location_at(poi["lat"], poi["lng"])

            item = SgRecord(
                locator_domain="watermillexpress.com",
                page_url="https://watermillexpress.com/locations/",
                location_name=poi["store"],
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zip"],
                country_code="US",
                store_number=poi["store"],
                phone=poi["phone"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
