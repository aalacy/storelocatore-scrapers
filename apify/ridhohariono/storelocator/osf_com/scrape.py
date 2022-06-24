from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "osf.com"
BASE_URL = "https://www.osf.com/"
LOCATION_URL = "https://www.osf.com/location/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("a", {"class": "e-link"})
    for li in contents:
        page_url = li["href"]
        store = pull_content(page_url)
        location_name = store.find(
            "h1", {"class": "m-pageHeader_location__title"}
        ).text.strip()
        madd = (
            store.find("p", {"class": "m-pageHeader_location__address"})
            .text.strip()
            .split(",")
        )
        street_address = madd[0].strip()
        if len(madd) == 4:
            street_address += " " + madd[1]
            del madd[1]
        city = madd[1].strip()
        state = madd[2].strip().split(" ")[0].strip()
        zip_postal = madd[2].strip().split(" ")[1].strip()
        country_code = "US"
        latitude = MISSING
        longitude = MISSING
        phone = store.find("p", {"class": "m-pageHeader_location__phone"}).text.strip()
        try:
            hoo = " ".join(
                list(
                    store.find(
                        "div", {"class": "m-pageHeader_location__hours"}
                    ).stripped_strings
                )
            ).strip()
            hours_of_operation = re.sub(r"Please note.*reservation\.", "", hoo).strip()
        except:
            hours_of_operation = MISSING
        location_type = MISSING
        if "TEMPORARILY" in hours_of_operation:
            hours_of_operation = re.sub(
                r"This location.+-flow-1", "", hours_of_operation
            ).strip()
            location_type = "TEMP_CLOSED"
        store_number = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
