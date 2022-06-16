from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "gorjana.com"
BASE_URL = "https://gorjana.com"
LOCATION_URL = "https://gorjana.com/pages/store-locator"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select(
        "div.stores_desktop div.store span.store__title.title-medium a"
    )
    for row in contents:
        page_url = BASE_URL + row["href"]
        if "/pages/" in page_url and "/pages/store-locator" not in page_url:
            info = pull_content(page_url)
            location_name = row.text.strip()
            addr = info.find_all(
                "div",
                {
                    "class": "elm text-edit gf-elm-left gf-elm-center-lg gf-elm-center-md gf-elm-center-sm gf-elm-center-xs"
                },
            )
            ptext = addr[2].text.strip()
            if "LEARN MORE" in ptext:
                raw_address = addr[0].get_text(strip=True, separator=",").rstrip(",")
                street_address, city, state, zip_postal = getAddress(raw_address)
                phone = addr[1].text.strip()
                hrs = info.find_all(
                    "div",
                    {
                        "class": "elm text-edit gf-elm-center-lg gf-elm-center-md gf-elm-center-sm gf-elm-center-xs gf-elm-center"
                    },
                )
                hours_of_operation = hrs[0].get_text(strip=True, separator=",")
            else:
                raw_address = addr[1].get_text(strip=True, separator=",").rstrip(",")
                street_address, city, state, zip_postal = getAddress(raw_address)
                phone = addr[2].text.strip()
                hours_of_operation = addr[0].get_text(strip=True, separator=",")
            country_code = "US"
            store_number = MISSING
            location_type = MISSING
            latitude = MISSING
            longitude = MISSING
            log.info("Append {} => {}".format(location_name, street_address))
            if "glendale-store-details" in page_url or "Glendale" in location_name:
                street_address = "773 Americana Way, Suite E15"
                city = "Glendale"
                state = "CA"
                zip_postal = "91210"
                phone = "(818) 409-9338"
                hours_of_operation = (
                    "Mon-Thurs: 11AM - 8PM; Fri-Sat: 10AM - 8PM; Sun: 11AM - 8PM"
                )
            hours = hours.replace("PMT", "PM,T").replace("PMS", "PM,S")
            if "Mon" not in hours_of_operation and "Sun" not in hours_of_operation and "Sat" not in hours_of_operation:
                tempphone = hours_of_operation
                hours_of_operation = phone
                phone = tempphone
            if state != "<MISSING>":
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
