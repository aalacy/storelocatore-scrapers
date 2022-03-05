from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "superbafoodandbread.com"
BASE_URL = "https://www.lifesuperba.com"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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
    HEADERS["Referer"] = url
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except:
        log.info("[RETRY] Pull content => " + url)
        pull_content(url)
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = soup.select("div#SubMenu-3 ul li a")
    for row in contents:
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        info = store.find("section", id="intro")
        location_name = row.text.strip()
        raw_address = info.find("a", {"data-bb-track-category": "Address"}).get_text(
            strip=True, separator=","
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        phone = info.find("a", {"data-bb-track-category": "Phone Number"}).text.strip()
        store_number = MISSING
        hoo = ""
        for hours in info.find_all("p")[1:]:
            hoo += (
                hours.get_text(strip=True, separator=",").replace("day,", "day: ")
                + ", ".strip()
            )
        hours_of_operation = (
            hoo.replace("** Modified Hours Until Further Notice**,", "")
            .rstrip(",")
            .strip()
        )
        latlong = store.find("div", {"class": "gmaps"})
        latitude = latlong["data-gmaps-lat"]
        longitude = latlong["data-gmaps-lng"]
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
