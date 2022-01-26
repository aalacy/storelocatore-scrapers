from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import re

DOMAIN = "inspirahealthnetwork.com"
BASE_URL = "https://www.inspirahealthnetwork.org"
LOCATION_URL = "https://www.inspirahealthnetwork.org/locations?page={}"
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
    num = 0
    while True:
        soup = pull_content(LOCATION_URL.format(num))
        contents = soup.select("div.location__info h2 a")
        if not contents:
            break
        for row in contents:
            page_url = BASE_URL + row["href"]
            store = pull_content(page_url)
            info = json.loads(
                store.find("script", {"type": "application/ld+json"}).string
            )
            location_name = info["name"].replace(" ", " ").strip()
            street_address = info["address"]["streetAddress"].replace("\n", ",").strip()
            city = info["address"]["addressLocality"]
            state = info["address"]["addressRegion"]
            zip_postal = info["address"]["postalCode"]
            country_code = "US"
            try:
                phone = re.sub(
                    r"ext.*|Get.*",
                    "",
                    store.find(
                        "span", {"class": "paragraph--type--phone-number--label"}
                    )
                    .find_next("a")
                    .text.strip(),
                ).strip()
            except:
                phone = MISSING
            store_number = MISSING
            try:
                hours_of_operation = info["openingHours"].strip()
            except:
                hours_of_operation = MISSING
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
        num += 1


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
