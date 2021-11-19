from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import json


DOMAIN = "nationwidevision.com"
BASE_URL = "https://nationwidevision.com"
LOCATION_URL = "https://www.nationwidevision.com/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).string)
    for row in data["props"]["pageProps"]["locations"]:
        page_url = LOCATION_URL + row["slug"]
        content = pull_content(page_url)
        info = json.loads(
            content.find("script", {"type": "application/ld+json"}).string
        )
        location_name = row["name"]
        street_address = info["address"]["streetAddress"]
        city = info["address"]["addressLocality"]
        state = info["address"]["addressRegion"]
        zip_postal = info["address"]["postalCode"]
        phone = info["telephone"].replace("+1-", "")
        hours_of_operation = (
            content.find("div", {"class": "w-full md:w-2/3 mt-4"})
            .get_text(strip=True, separator=",")
            .replace(",This location is now accepting new patients", "")
            .replace("day,", "day: ")
        )
        country_code = info["address"]["addressCountry"]
        store_number = MISSING
        location_type = info["@type"]
        latitude = info["geo"]["latitude"]
        longitude = info["geo"]["longitude"]
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
