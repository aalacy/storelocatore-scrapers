import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import json

DOMAIN = "spar.hr"
BASE_URL = "https://www.spar.hr"
SITEMAP = "https://www.spar.hr/lokacije.sitemap.xml"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
MISSING = "<MISSING>"


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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITEMAP)
    page_urls = soup.find_all("loc")
    for row in page_urls:
        page_url = row.text
        if page_url == "https://www.spar.hr/lokacije":
            continue
        store = pull_content(page_url)
        info = store.find(
            "script",
            type="application/ld+json",
            string=re.compile(r"openingHoursSpecification.*"),
        ).string
        info = json.loads(info)
        location_name = info["name"]
        street_address = info["address"]["streetAddress"]
        city = info["address"]["addressLocality"]
        state = info["address"]["addressRegion"]
        zip_postal = info["address"]["postalCode"]
        phone = info["telephone"].replace("01/", "")
        store_number = MISSING
        location_type = info["@type"]
        hours_of_operation = ""
        for hoo in info["openingHoursSpecification"]:
            day = hoo["dayOfWeek"].replace("http://schema.org/", "")
            if day in hours_of_operation:
                continue
            hours_of_operation += (
                day + ": " + hoo["opens"] + " - " + hoo["closes"] + ","
            )
        hours_of_operation = re.sub(r",$", "", hours_of_operation).lstrip(",")
        country_code = "HR"
        latitude = info["geo"]["latitude"]
        longitude = info["geo"]["longitude"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
