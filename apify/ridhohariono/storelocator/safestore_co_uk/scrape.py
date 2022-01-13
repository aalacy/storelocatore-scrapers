from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "safestore.co.uk"
BASE_URL = "https://www.safestore.co.uk"
LOCATION_URL = "https://www.safestore.co.uk/storage-near-me/"
API_ENDPOINT = "https://www.safestore.co.uk/search.ashx?action=search-in-area"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return 404
    soup = bs(req.content, "lxml")
    return soup


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


def get_hoo(url):
    soup = pull_content(url)
    content = soup.find("div", {"class": "store-info__time"}).find_all(
        "div", {"class": "grid__item grid__item_span_3"}
    )
    day = content[0].find_all("p")
    hours = content[1].find_all("p")
    hoo = []
    for i in range(len(day)):
        hoo.append((day[i].text.replace("\r", "") + hours[i].text).strip())
    return ", ".join(hoo)


def fetch_data():
    log.info("Fetching store_locator data")
    data = {
        "northeast[latitude]": 49,
        "northeast[longitude]": 8,
        "southwest[latitude]": 61,
        "southwest[longitude]": 2,
    }
    store_info = session.post(
        API_ENDPOINT, headers=HEADERS, data=data, verify=False, timeout=100
    ).json()
    for row in store_info["stores"]:
        page_url = BASE_URL + row["DetailsUrl"]
        location_name = row["StoreName"]
        raw_address = row["Address"]
        street_address, city, state, _ = getAddress(raw_address)
        if state == "G4":
            state = MISSING
        zip_postal = row["Postcode"]
        country_code = "GB"
        store_number = row["Id"]
        phone = row["Phone"]
        hours_of_operation = get_hoo(page_url)
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
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
