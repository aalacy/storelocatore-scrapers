from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

MISSING = "<MISSING>"

DOMAIN = "ghirardelli.com"
BASE_URL = "https://ghirardelli.com/"
LOCATION_URL = "https://www.ghirardelli.com/wcsstore/storelocator-data/gcc_locations.json?origLat=37.721008&origLng=-122.501943&origAddress=Horse%2520Trail%252C%2520San%2520Francisco%252C%2520CA%252094132%252C%2520Amerika%2520Serikat&formattedAddress=&boundsNorthEast=&boundsSouthWest=&storeId=11003&langId=-1&origLat=37.721008&origLng=-122.501943&origAddress=Horse%2520Trail%252C%2520San%2520Francisco%252C%2520CA%252094132%252C%2520Amerika%2520Serikat&formattedAddress=&boundsNorthEast=&boundsSouthWest="
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def parse_hours(url):
    soup = pull_content(url)
    hours_content = soup.find("div", {"class": "panel"})
    if not hours_content:
        hours_content = soup.find("table")
    if not hours_content.find("table"):
        check = hours_content.text
        if "Temporarily closed" in check:
            return MISSING
    else:
        hours_content = hours_content.find("table")
    hours = hours_content.get_text(strip=True, separator=",").replace("day,", "day: ")
    if "Temporarily Closed" in hours:
        return MISSING
    hoo = re.sub(
        r"Ice cream fountain opens daily at \d{1,2}:\d{2} \D{2},|Park Hours at Disneyland California",
        "",
        hours,
    )
    return hoo


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    for row in store_info:
        page_url = row["web"]
        location_name = row["name"]
        if "address2" in row and len(row["address2"]) > 0:
            street_address = "{}, {}".format(row["address"], row["address2"])
        else:
            street_address = row["address"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal"]
        country_code = "US"
        store_number = row["id"]
        phone = row["phone"]
        latitude = row["lat"]
        longitude = row["lng"]
        hours_of_operation = parse_hours(page_url)
        location_type = MISSING
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
