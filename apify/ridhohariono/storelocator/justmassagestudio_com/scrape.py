from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "justmassagestudio.com"
BASE_URL = "https://justmassagestudio.com/"
LOCATION_URL = "https://justmassagestudio.com/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = SgRecord.MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(soup):
    pattern = re.compile(r"window\.wsb\[(.*)\]", re.MULTILINE | re.DOTALL)
    script = soup.find_all("script", text=pattern)
    if len(script) == 0:
        return MISSING, MISSING
    parse = re.search(
        r'"lat\\":\\"(-?\d+(\.\d+)?)\\",\\"lon\\":\\"\s*(-?\d+(\.\d+)?)\\"',
        script[3].string,
    )
    if not parse:
        parse = re.search(
            r'"lat\\":(-?\d+(\.\d+)?),\\"lon\\":\s*(-?\d+(\.\d+)?)', script[3].string
        )
    if not parse:
        return MISSING, MISSING
    latitude = parse.group(1)
    longitude = parse.group(3)
    return latitude, longitude


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = [BASE_URL + "el-segundo", BASE_URL + "westchester"]
    for page_url in store_urls:
        soup = pull_content(page_url)
        content = soup.find("div", {"data-aid": "CONTACT_INFO_CONTAINER_REND"})
        location_name = content.find("h4").text
        address = (
            content.find("p", {"data-aid": "CONTACT_INFO_ADDRESS_REND"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        street_address = address[0]
        city = address[1]
        state_zip = address[2].split()
        state = state_zip[0]
        zip_postal = state_zip[1]
        phone = content.find("a", {"data-aid": "CONTACT_INFO_PHONE_REND"}).text
        hours_of_operation = (
            content.find("div", {"data-aid": "CONTACT_HOURS_CUST_MSG_REND"})
            .get_text(strip=True, separator=" ")
            .split("CLOSED ON:")[0]
            .strip()
        )
        store_number = MISSING
        country_code = "US"
        location_type = "justmassagestudio"
        latitude, longitude = get_latlong(soup)
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
