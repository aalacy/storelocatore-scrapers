from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "iroparis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.iroparis.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
        )
        for lat, long in search:
            log.info(f"Fetching Locations for lat {lat} & long {long}")
            url = (
                "https://www.iroparis.com/on/demandware.store/Sites-IRO-us-Site/en_US/Stores-FindStores?showMap=false&lat="
                + str(lat)
                + "&long="
                + str(long)
                + "&radius=300.0"
            )
            loclist = session.get(url, headers=headers).json()["stores"]
            if not loclist:
                continue
            for loc in loclist:
                location_name = loc["name"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                hours_of_operation = loc["storeHours"]
                hours_of_operation = (
                    BeautifulSoup(hours_of_operation, "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                phone = loc["phone"]
                street_address = loc["address1"]
                log.info(street_address)
                city = loc["city"]
                try:
                    state = loc["stateCode"]
                except:
                    state = MISSING
                zip_postal = loc["postalCode"]
                country_code = loc["countryCode"]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.iroparis.com/us/stores",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
