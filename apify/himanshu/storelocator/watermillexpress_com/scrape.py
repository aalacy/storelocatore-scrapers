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
        expected_search_radius_miles=5,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    for lat, lng in coords:

        location_url = (
            "https://watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=250&search_radius=10&search=&statistics="
        )
        try:
            r_locations = session.get(location_url, headers=headers)
            json_data = r_locations.json()
        except Exception:
            continue

        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = "<MISSING>"
        page_url = (
            "http://www.watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=250&search_radius=10&search=&statistics="
        )

        for location in json_data:
            city = location["city"]
            state = location["state"]
            zipp = location["zip"]
            address2 = location["address2"]
            street_address = (
                location["address"] + " " + str(address2).replace("None", "")
            )
            latitude = location["lat"]
            longitude = location["lng"]
            phone = location["phone"]
            store_number = location["store"]
            hours_of_operation = "Open 24/7"

            item = SgRecord(
                locator_domain="watermillexpress.com",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
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
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
