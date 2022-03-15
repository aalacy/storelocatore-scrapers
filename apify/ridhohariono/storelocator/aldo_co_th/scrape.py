from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "aldo.co.th"
LOCATION_URL = "https://www.aldo.co.th/en/store-locator"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_phone(url):
    soup = pull_content(url)
    phone = soup.find("a", {"class": "font-bold underline contact-link"})
    if not phone:
        return MISSING
    return phone.text.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("div", id="mw-sl__stores__list_block").find_all("li")
    for row in contents:
        page_url = row.find("div", {"class": "mw-sl__stores__list__item__right"}).find(
            "a"
        )["href"]
        store = pull_content(page_url).find(
            "div", {"id": "mw-store-locator-details-page"}
        )
        location_name = row.find(
            "span", {"class": "mw-sl__store__info__name"}
        ).text.strip()
        raw_address = " ".join(
            store.find(
                "div", {"class": "mw-sl__details__item mw-sl__details__item--location"}
            )
            .get_text(strip=True, separator=",")
            .replace("Address,", "")
            .split()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        try:
            phone = store.find(
                "a", {"class": "font-bold underline contact-link"}
            ).text.strip()
        except:
            phone = MISSING
        country_code = "TH"
        location_type = MISSING
        store_number = row["id"]
        hoo_table = row.find("table", {"class": "mw-sl__stores__details__hours__table"})
        hoo_table.find("tr").decompose()
        hours_of_operation = hoo_table.get_text(strip=True, separator=",").replace(
            "day,", "day: "
        )
        latitude = row["data-lat"]
        longitude = row["data-long"]
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
