from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re


DOMAIN = "connor.com.au"
BASE_URL = "https://www.connor.com.au/au"
API_URL = "https://www.connor.com.au/au/stores/index/dataAjax/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
    data = session.post(API_URL, headers=HEADERS).json()
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for row in data:
        page_url = BASE_URL + row["u"]
        store = pull_content(page_url)
        location_name = row["n"].strip()
        street_address = row["a"][0]
        city = row["a"][1]
        state = row["a"][3]
        zip_postal = row["a"][2]
        country_code = "AU"
        phone = row["p"]
        hoo = ""
        try:
            hours = re.sub(r"\d{1}\|", "", row["oh"]).split(",")
            for i in range(len(days)):
                hoo += days[i] + ": " + hours[i] + ", "
            hours_of_operation = hoo.strip().rstrip(",")
        except:
            hours_of_operation = MISSING
        try:
            type = (
                store.find("div", {"class": "categories"})
                .text.replace("\n", ",")
                .strip()
            )
            if "Retail Store" in type:
                location_type = "Retail Store"
            elif "Outlet Store" in type:
                location_type = "Outlet Store"
        except:
            location_type = MISSING
        store_number = row["i"]
        latitude = row["l"]
        longitude = row["g"]
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
