from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "massageheights.com"
BASE_URL = "https://www.massageheights.com"
API_URL = "https://www.massageheights.com/locations/?CallAjax=GetLocations"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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


def get_hoo(soup):
    hoo = ""
    try:
        hoo_content = soup.find(
            "div", {"class": "hero-hours half flex ui-repeater"}
        ).find_all("span", {"data-item": "i"})
        for hday in hoo_content:
            hoo += hday.text.strip() + ", "
        hoo = " ".join(hoo.split())
    except:
        return MISSING
    return hoo.strip().rstrip(",")


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        if row["ComingSoon"] == 1:
            continue
        page_url = BASE_URL + row["Path"]
        store = pull_content(page_url)
        is_coming_soon = store.find(
            "em", text=re.compile(r"Coming Soon", flags=re.IGNORECASE)
        )
        if is_coming_soon:
            continue
        location_name = row["FranchiseLocationName"]
        street_address = (row["Address1"] + " " + row["Address2"]).strip()
        city = row["City"]
        state = row["State"]
        zip_postal = row["ZipCode"]
        phone = row["Phone"]
        country_code = "US" if row["Country"] == "USA" else row["Country"]
        store_number = row["FranchiseLocationID"]
        hours_of_operation = MISSING
        hours_of_operation = get_hoo(store)
        latitude = row["Latitude"]
        longitude = row["Longitude"]
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
