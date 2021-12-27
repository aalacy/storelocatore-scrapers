from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import json

DOMAIN = "devere.co.uk"
BASE_URL = "https://www.devere.co.uk/"
LOCATION_URL = "https://www.devere.co.uk/destinations/"
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
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.destination-link a")
    for row in contents:
        page_url = row["href"]
        if page_url == BASE_URL:
            continue
        elif "nottingham-conferences" in page_url:
            page_url = "https://www.devere.co.uk/nottingham-conferences"
            info = pull_content(
                "https://www.nottinghamconferences.co.uk/Contact/Home.aspx"
            )
            location_name = row.text.strip()
            raw_address = (
                info.find("address")
                .get_text(strip=True, separator=",")
                .replace("Nottingham Conferences Cottage,", "")
                .replace("University of Nottingham,", "")
                .replace("Nottingham Conferences,", "")
            ).strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = info.find("span", {"class": "icon-call"}).text.strip()
            location_type = MISSING
            country_code = "GB"
            latitude = MISSING
            longitude = MISSING
        else:
            info = json.loads(
                pull_content(page_url)
                .find("script", {"type": "application/ld+json"})
                .string
            )
            location_name = info["name"]
            street_address = info["address"]["streetAddress"].strip()
            city = info["address"]["addressLocality"]
            state = MISSING
            zip_postal = info["address"]["postalCode"]
            country_code = (
                "GB"
                if info["address"]["addressCountry"] == "England"
                else info["address"]["addressCountry"]
            )
            phone = info["telephone"][0]
            location_type = info["@type"]
            latitude = info["geo"]["latitude"]
            longitude = info["geo"]["longitude"]
        store_number = MISSING
        hours_of_operation = MISSING
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
