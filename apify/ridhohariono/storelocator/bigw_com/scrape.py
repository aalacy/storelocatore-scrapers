from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json


DOMAIN = "bigw.com.au"
BASE_URL = "https://www.bigw.com.au/store/"
STORE_URL = "https://www.bigw.com.au/store/0552/BIG-W-Parabanks"
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
    soup = pull_content(STORE_URL)
    data = json.loads(soup.find("script", id="__NEXT_DATA__").string)["props"][
        "pageProps"
    ]["serializedData"]["store"]
    for key, val in data.items():
        page_url = BASE_URL + val["id"] + "/" + val["name"].replace(" ", "-")
        location_name = val["name"]
        street_address = val["address"]["street"]
        city = val["address"]["suburb"]
        state = val["address"]["state"]
        zip_postal = val["address"]["postcode"]
        country_code = "AU"
        phone = val["phoneNumber"]
        hoo = ""
        for day, hour in val["openingHours"]["hours"].items():
            hoo += day + ": " + hour + ", "
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        store_number = val["id"]
        latitude = val["location"]["lat"]
        longitude = val["location"]["lng"]
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
