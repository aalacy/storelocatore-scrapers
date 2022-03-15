from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re


DOMAIN = "marrybrown.com"
BASE_URL = "https://marrybrown.com"
LOCATION_URL = "https://marrybrown.com/locations/"
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
    contents = soup.select("section.location-result")
    for row in contents:
        info = row.select("div.elementor-text-editor.elementor-clearfix")
        location_name = info[0].text.strip()
        zip_city_state = (
            re.sub(
                r",?\s+?Malaysia",
                "",
                row.select_one("section.location-result div.location-search-data").text,
                flags=re.IGNORECASE,
            )
            .strip()
            .split(",")
        )
        if len(zip_city_state) < 3:
            city = re.sub(r"\d+", "", zip_city_state[0].strip())
            state = zip_city_state[1].replace(".", "").strip()
            zip_postal = re.sub(r"\D+", "", zip_city_state[0].strip())
        else:
            city = zip_city_state[1].strip()
            state = zip_city_state[2].replace(".", "").strip()
            zip_postal = zip_city_state[0].strip()
        street_address = (
            re.sub(
                state + r"|" + str(zip_postal),
                "",
                info[1].get_text(strip=True, separator=",").replace("\n", " ").strip(),
            )
            .strip()
            .rstrip(",")
        )
        phone = (
            " ".join(info[3].text.replace("–", " ").split())
            .replace("TBA", "")
            .strip()
            .split("/")[0]
            .split(",")[0]
        ) or MISSING
        country_code = MISSING
        hours_of_operation = (
            info[2].get_text(strip=True, separator=",").replace("\n", " ").strip()
        )
        latitude = row.select_one(
            "section.location-result div.location-latitude"
        ).text.strip()
        longitude = row.select_one(
            "section.location-result div.location-longitude"
        ).text.strip()
        location_type = MISSING
        store_number = row.parent.parent.parent["data-post-id"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
