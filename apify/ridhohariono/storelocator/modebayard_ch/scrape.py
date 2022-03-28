from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re


DOMAIN = "modebayard.ch"
BASE_URL = "https://modebayard.ch"
LOCATION_URL = "https://www.modebayard.ch/de/store-locator"
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
    contents = soup.select("ul#list-store-detail li a.action")
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        info = store.find("div", {"class": "store-info"})
        location_name = info.find("h3").text.strip()
        raw_address = info.find("p", {"class": "address-store"}).get_text(
            strip=True, separator=","
        )
        addr = raw_address.split(",")
        street_address = ", ".join(addr[:-1]).strip()
        city = re.sub(r"\d+", "", addr[-1]).strip()
        state = MISSING
        zip_postal = addr[-1].split(" ")[0].strip()
        phone = info.find("a", {"class": "store-pickup-phone"}).text.strip()
        country_code = "CH"
        hours_of_operation = (
            store.find("div", id="open_hour")
            .find("table")
            .get_text(strip=True, separator=",")
            .replace(":,", ": ")
            .strip()
        )
        latlong = store.find("script", string=re.compile("distanceunit=.*")).string
        latitude = latlong.split("lat:")[1].split(",lng:")[0]
        longitude = latlong.split(",lng:")[1].split(",name:")[0]
        location_type = MISSING
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
            raw_address=raw_address,
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
