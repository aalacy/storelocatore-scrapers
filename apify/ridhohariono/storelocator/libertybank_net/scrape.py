from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "libertybank.com"
BASE_URL = "https://www.libertybank.com"
LOCATION_URL = "https://www.libertybank.net/customer_care/locations/"
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


def parse_hours(table):
    results = []
    if table:
        th = table.find_all("th")
        del th[0]
        opens = table.find_all("tr")[1].find_all("td")
        del opens[0]
        closes = table.find_all("tr")[2].find_all("td")
        del closes[0]
        for i in range(len(opens)):
            hoo = "{}: {} - {}".format(
                th[i].text.strip(), opens[i].text.strip(), closes[i].text
            )
            results.append(hoo)
    return ", ".join(results)


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"id": "location-type-2"})
    links = content.find_all("a", text="View Site")
    for link in links:
        store_urls.append(LOCATION_URL + link["href"])
    log.info("Found {} store URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    for page_url in page_urls:
        soup = pull_content(page_url)
        location_name = "Liberty Bank"
        content = soup.find_all("a", {"href": re.compile(r"tel:.*")})
        if len(content) > 1:
            content = content[-1]
        else:
            content = content[0]
        get_parent = content.parent("p")
        if get_parent:
            address = (
                get_parent[0]
                .get_text(strip=True, separator=",")
                .replace(" - at ", " - at,")
                .replace(" – at ", " – at,")
                .split(",")
            )
            if len(address) > 3:
                del address[0]
        else:
            address = content.parent.get_text(strip=True, separator=",").split(",")
        raw_address = ",".join(address[:3]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
        phone = content.text.strip()
        location_type = "BRANCH"
        try:
            map_link = soup.find("iframe", {"src": re.compile(r"\/maps\/embed\?.*")})[
                "src"
            ]
            latitude, longitude = get_latlong(map_link)
        except:
            latitude = MISSING
            longitude = MISSING
        hours_of_operation = parse_hours(
            soup.find("h2", text=re.compile(r"Lobby Hours")).find_next("table")
        )
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
