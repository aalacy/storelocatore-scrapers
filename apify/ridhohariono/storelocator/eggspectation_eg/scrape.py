from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "eggspectation.eg"
BASE_URL = "https://www.eggspectation.eg/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = soup.select("footer#colophon ul li a")
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        info = (
            store.find("footer", id="colophon")
            .find("div", {"class": "column column-2"})
            .find_all("p")
        )
        location_name = row.text.strip()
        raw_address = info[0].get_text(strip=True, separator=",").replace(",,", ",")
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "Cairo" in raw_address:
            city = "Cairo"
        phone = (
            store.find("footer", id="colophon")
            .find("a", {"class": "phone-number"})
            .text.strip()
        )
        country_code = "EG"
        store_number = MISSING
        try:
            hours_of_operation = (
                store.find("div", {"class": "hours-wrapper"})
                .find("table")
                .get_text(strip=True, separator=",")
                .replace("am,", "am - ")
                .replace("Mon,", "Mon: ")
                .replace("Sun,", "Sun: ")
                .replace("Tue,", "Tue: ")
                .replace("Wed,", "Wed: ")
                .replace("Thu,", "Thu: ")
                .replace("Fri,", "Fri: ")
                .replace("Sat,", "Sat: ")
            ).strip()
        except:
            hours_of_operation = MISSING
        try:
            latlong = (
                store.find("a", {"class": "directions"})["href"]
                .split("&daddr=")[1]
                .split(",")
            )
            latitude = latlong[0]
            longitude = latlong[1]
        except:
            latitude = MISSING
            longitude = MISSING
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
