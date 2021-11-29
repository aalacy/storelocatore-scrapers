from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import re

DOMAIN = "herfy.com"
LOCATION_URL = "https://www.herfy.com/pages/store-locator/pgid-1341541.aspx"
API_STATE = "https://www.herfy.com/WebAPI/Location/Country/SA/States"
API_SINGLE_STORE = "https://www.herfy.com/WebAPI/Location/Search?Channel=W&state={}&TemplateId=123&searchby=state&filters=state&Format=html&CurrentEvent=Location_Search"
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
    state_name = json.loads(session.get(API_STATE, headers=HEADERS).json()["StateList"])
    for api_state in state_name:
        url = API_SINGLE_STORE.format(api_state["StateCode"])
        data = bs(session.get(url, headers=HEADERS).json(), "lxml")
        try:
            stores = data.find("ul").find_all("li")
        except:
            continue
        for row in stores:
            info = (
                row.find("div", {"class": "store-address"})
                .get_text(strip=True, separator="@@")
                .split("@@")
            )
            location_name = info[0].strip()
            street_address = info[1].strip()
            city = api_state["StateName"]
            state = MISSING
            zip_postal = MISSING
            phone = (
                row.find("div", {"class": "store-phone"})
                .text.replace("\n", "")
                .replace("Phone number", "")
                .strip()
            )
            country_code = "SA"
            hours_of_operation = MISSING
            location_type = MISSING
            store_number = re.sub(r"\D+", "", location_name)
            latlong = row.find("a", {"class": "map-view-scl"})
            latitude = (
                MISSING
                if latlong["data-latitude"] == "0.0"
                else latlong["data-latitude"]
            )
            longitude = (
                MISSING
                if latlong["data-longitude"] == "0.0"
                else latlong["data-longitude"]
            )
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
