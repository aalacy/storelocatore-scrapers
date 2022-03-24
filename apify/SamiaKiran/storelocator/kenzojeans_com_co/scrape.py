import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicGeoSearch
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import SearchableCountries
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "kenzojeans_com_co"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://kenzojeans.com.co/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.COLOMBIA],
            max_search_results=100,
            expected_search_radius_miles=200,
        )
        for lat, long in search:
            url = (
                "https://kenzojeans.com.co/wp-admin/admin-ajax.php?action=store_search&lat="
                + str(lat)
                + "&lng="
                + str(long)
                + "&max_results=100&search_radius=500"
            )
            loclist = session.get(url, headers=headers).json()
            for loc in loclist:
                location_name = loc["store"]
                log.info(location_name)
                store_number = loc["id"]
                phone = loc["phone"]
                street_address = loc["address"] + " " + loc["address2"]
                street_address = strip_accents(street_address)
                city = strip_accents(loc["city"])
                state = loc["state"]
                zip_postal = loc["zip"]
                country_code = loc["country"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                hours_of_operation = strip_accents(
                    BeautifulSoup(loc["hours"], "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                raw_address = street_address + " " + city + " " + zip_postal
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://kenzojeans.com.co/tiendas/",
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


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
