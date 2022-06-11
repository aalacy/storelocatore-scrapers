import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "stewartsshops_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.stewartsshops.com"
MISSING = SgRecord.MISSING


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=300,
        expected_search_radius_miles=200,
    )
    for lat, long in search:
        log.info(f"Coordinates remaining: {search.items_remaining()})")
        url = (
            "https://www.stewartsshops.com/wp-admin/admin-ajax.php?action=store_search&distance_unit=mi&lat="
            + str(lat)
            + "&lng="
            + str(long)
            + "&max_results=300&search_radius=200"
        )
        loclist = session.get(url, headers=headers).json()
        if loclist:
            for loc in loclist:
                location_name = html.unescape(loc["store"])
                page_url = loc["permalink"]
                log.info(location_name)
                store_number = location_name.split("#", 1)[1].replace("-", "")
                if store_number.split():
                    store_number = store_number.split()[0]
                street_address = loc["address"].replace("Watervliet NY 12189", "")
                city = loc["city"]
                state = loc["state"]
                zip_postal = loc["zip"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                phone = loc["phone"]
                phone = phone.split("|", 1)[0]
                country_code = "US"
                hours_of_operation = (
                    BeautifulSoup(loc["hours"], "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
