from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json

DOMAIN = "maxphoto.co.uk"
BASE_URL = "https://www.maxphoto.co.uk"
LOCATION_URL = "https://www.maxphoto.co.uk/photo-store-locator/"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.storefinder-storelist-a-z a")
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for row in contents:
        page_url = BASE_URL + row["href"]
        info = pull_content(page_url)
        store_contents = info.find("script", string=re.compile(r"var\s+lpr_vars\s+=.*"))
        store = json.loads(
            re.search(
                r"var\s+lpr_vars\s+=\s+(.*)\nvar\s+lpr_groups", store_contents.string
            ).group(1)
        )["initial_location"]
        location_name = store["name"]
        if "street2" in store:
            street_address = (store["street1"] + " " + store["street2"]).strip()
        else:
            street_address = store["street1"]
        city = store["city"]
        if "state" not in store:
            state = MISSING
        else:
            state = store["state"]
        zip_postal = store["zip"]
        country_code = "UK"
        phone = store["phone"]
        store_number = store["store_no"]
        hoo = ""
        temp_hour = []
        for i in range(len(days)):
            hour = store["opening_" + str(i + 1)]
            if not hour:
                hour = "CLOSED"
            hoo += days[i] + ": " + hour + ","
            temp_hour.append(hour)
        if all(value == "CLOSED" for value in temp_hour):
            hours_of_operation = MISSING
        else:
            hours_of_operation = hoo.rstrip(",")
        latitude = store["latitude"]
        longitude = store["longitude"]
        location_type = "Photo centre"
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
