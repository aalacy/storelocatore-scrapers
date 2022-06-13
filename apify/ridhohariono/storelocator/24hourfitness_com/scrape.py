from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "24hourfitness.com"
BASE_URL = "https://24hourfitness.com/Website/Club/{}"
LOCATION_URL = "https://www.24hourfitness.com"
API_URL = "https://www.24hourfitness.com/Website/ClubLocation/OpenClubs/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(url):
    soup = pull_content(url)
    try:
        content = soup.find("div", id="club-hours-details")
        if "Open 24 hours per day" in content.text.strip():
            hoo = "Open 24 hours per day"
        else:
            hoo = (
                content.find("table")
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
            )
    except:
        return MISSING
    return hoo.rstrip(",").strip()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["clubs"]:
        store_number = row["clubNumber"]
        page_url = BASE_URL.format(store_number)
        location_name = row["name"].strip()
        street_address = (
            row["address"]["street"].replace(" ", "").replace("\n", ",").strip()
        )
        city = row["address"]["city"]
        state = row["address"]["state"]
        zip_postal = row["address"]["zip"]
        phone = row["phoneNumber"]
        hours_of_operation = get_hoo(page_url)
        location_type = row["type"]
        country_code = "US"
        latitude = row["coordinate"]["latitude"]
        longitude = row["coordinate"]["longitude"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
