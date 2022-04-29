from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "darty.com"
BASE_URL = "https://magasin.darty.com"
LOCATION_URL = "https://magasin.darty.com/fr?page={}"
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 500:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    num = 1
    while True:
        soup = pull_content(LOCATION_URL.format(num))
        if not soup:
            break
        contents = soup.select(
            "a.lf-geo-divisions__results__content__locations__list__item__link"
        )
        for row in contents:
            page_url = BASE_URL + row["href"]
            store = pull_content(page_url)
            location_name = store.find(
                "h1", {"class": "lf-location__store__flash__infos__title"}
            ).text.strip()
            raw_address = store.find(
                "address", id="locations-address-default"
            ).get_text(strip=True, separator=",")
            street_address, city, state, zip_postal = getAddress(raw_address)
            try:
                phone = (
                    store.find("a", {"class": "lf-location-phone-default__phone"})[
                        "href"
                    ]
                    .replace("tel:", "")
                    .strip()
                )
            except:
                phone = MISSING
            country_code = "FR"
            hours_of_operation = store.find(
                "div", {"class": "lf-location-opening-hours-default__row"}
            ).get_text(strip=True, separator=" ")
            location_type = MISSING
            store_number = MISSING
            latitude = store.find("meta", {"property": "place:location:latitude"})[
                "content"
            ]
            longitude = store.find("meta", {"property": "place:location:longitude"})[
                "content"
            ]
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
        num += 1


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
