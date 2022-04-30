from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "ulsterbank.ie"
LOCATION_URL = "https://locator.ulsterbank.ie"
API_URL = "https://www.ulsterbank.ie/content/branchlocator/en/ulsterbank_roi/searchresults/_jcr_content/par/searchresults.search.html"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    req = session.get(LOCATION_URL)
    soup = bs(req.content, "lxml")
    csrf = soup.find("input", id="csrf-token")["value"]
    payload = {
        "CSRFToken": csrf,
        "lat": 53.1423672,
        "lng": -7.692053599999999,
        "site": "ulsterbank_roi",
        "pageDepth": 4,
        "search_term": "dublin",
        "searchMiles": 500,
        "offSetMiles": 1000,
        "maxMiles": 15000,
        "listSizeInNumbers": 10000,
        "search-type": 1,
    }
    req = session.post(API_URL, data=payload)
    contents = bs(req.content, "lxml").select("div.results-marker-link")
    for row in contents:
        page_url = LOCATION_URL + row.find("a")["href"]
        store = pull_content(page_url)
        location_name = (
            store.find("div", id="single-result-header")
            .find("div", {"class": "header left"})
            .text.strip()
        )
        table = store.find("table", id="results-table")
        table.find("tr").decompose()
        info = (
            table.get_text(strip=True, separator="@@")
            .replace("@@Customer support centre:", "")
            .split("@@")
        )
        raw_address = ",".join(info[:3]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = info[3].replace("Personal: ", "").strip()
        country_code = "IE"
        hoo = ""
        for hday in table.find_all("tr", {"class": "time"}):
            hoo += hday.get_text(strip=True, separator=" ").strip() + ","
        hours_of_operation = hoo.rstrip(",")
        location_type = "BRANCH"
        store_number = re.sub(r"\D+", "", location_name)
        latlong = (
            store.find("a", {"class": "email-location"})["href"]
            .split("maps?q=")[1]
            .split(",")
        )
        latitude = latlong[0]
        longitude = latlong[0]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
