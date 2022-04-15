from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


session = SgRequests()
website = "bargainbasementhomecenter_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://doctorsofphysicaltherapy.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        identities = set()
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA],
            max_search_distance_miles=1000,
            max_search_results=35,
        )
        for lat, long in search:
            url = (
                "https://doctorsofphysicaltherapy.com/wp-admin/admin-ajax.php?action=store_search&lat="
                + str(lat)
                + "&lng="
                + str(long)
                + "&autoload=1"
            )
            loclist = session.get(url, headers=headers).json()
            for loc in loclist:
                page_url = loc["permalink"]
                if "coming-soon" in page_url:
                    location_type = "Coming Soon"
                else:
                    location_type = MISSING
                phone = loc["phone"]
                location_name = loc["store"]
                hours_of_operation = loc["hours"]
                hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
                hours_of_operation = (
                    hours_of_operation.find("table")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                try:
                    street_address = loc["address"] + " " + loc["address2"]
                except:
                    street_address = loc["address"]
                city = loc["city"]
                zip_postal = loc["zip"]
                country_code = loc["country"]
                state = loc["state"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                if not state:
                    state = "MI"

                identity = (
                    str(zip_postal)
                    + ","
                    + str(state)
                    + ","
                    + str(street_address)
                    + ","
                    + str(city)
                )
                if identity not in identities:
                    identities.add(identity)
                    log.info(page_url)
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone.strip(),
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
