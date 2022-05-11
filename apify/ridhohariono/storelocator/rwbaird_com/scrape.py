import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re
import ssl
from sgselenium import SgSelenium

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "rwbaird.com"
BASE_URL = "https://rwbaird.com/"
LOCATION_URL = "https://www.rwbaird.com/who-we-are/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = SgRecord.MISSING


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
            country_code = data.country
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country_code is None or len(country_code) == 0:
                country_code = MISSING
            return street_address, city, state, zip_postal, country_code
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except:
        return False
    return soup


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    soup = bs(driver.page_source, "lxml")
    driver.quit()
    contents = soup.select("div.tab-content-container")
    for row in contents:
        location_type = row.find("h2").text.strip()
        if "PRIVATE WEALTH MANAGEMENT" in location_type:
            locations = row.select("div.row.no-mar-btm a")
            for location in locations:
                page_url = location["href"]
                try:
                    store = pull_content(page_url)
                    info = json.loads(
                        store.find("script", type="application/ld+json").string
                    )
                except:
                    continue
                location_name = info["name"]
                addr = info["address"]
                street_address = addr["streetAddress"].strip().rstrip(",")
                city = addr["addressLocality"]
                state = addr["addressRegion"]
                zip_postal = addr["postalCode"]
                country_code = addr["addressCountry"]
                phone = info["telephone"]
                country_code = "US"
                hours_of_operation = MISSING
                latitude = MISSING
                longitude = MISSING
                store_number = MISSING
                raw_address = f"{street_address}, {city}, {state}, {zip_postal}"
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
        else:
            locations = row.select("div.col.s12 p")
            for store in locations:
                page_url = LOCATION_URL
                if (
                    "With more than 35" in store.text.strip()
                    or "Baird Trust headquarters" in store.text.strip()
                    or "This part of our" in store.text.strip()
                    or "This unit consists" in store.text.strip()
                    or "Baird Capital has" in store.text.strip()
                ):
                    continue
                try:
                    phone_content = store.find("a", {"href": re.compile(r"tel.*")})
                    phone = phone_content.text.strip()
                    phone_content.decompose()
                except:
                    phone = MISSING
                info = (
                    store.get_text(strip=True, separator="@@")
                    .replace("@@*", "")
                    .replace("@@+", "")
                    .replace("@@Five Post Oak Park", "")
                    .split("@@")
                )
                location_name = info[0]
                total_len = len(info)
                if total_len > 6:
                    html_string = str(store).strip()
                    locations = html_string.split("<br/><br/>")
                    for store in locations:
                        store = bs(store, "lxml")
                        try:
                            phone_content = store.find(
                                "a", {"href": re.compile(r"tel.*")}
                            )
                            phone = phone_content.text.strip()
                            phone_content.decompose()
                        except:
                            phone = MISSING
                        info2 = (
                            store.get_text(strip=True, separator="@@")
                            .replace("@@*", "")
                            .replace("@@+", "")
                            .replace("@@Five Post Oak Park", "")
                            .replace(location_name + "@@", "")
                            .split("@@")
                        )
                        if (
                            "Research" in store.text.strip()
                            or "Equity Sales" in store.text.strip()
                            or "Investment Banking" in store.text.strip()
                        ):
                            location_name = info[0] + " " + info2[0]
                            del info2[0]
                        raw_address = re.sub(
                            r", Indianapolis, Indiana,.*", "", ", ".join(info2).strip()
                        ).strip()
                        (
                            street_address,
                            city,
                            state,
                            zip_postal,
                            country_code,
                        ) = getAddress(raw_address)
                        if country_code == MISSING:
                            country_code = "US"
                        hours_of_operation = MISSING
                        latitude = MISSING
                        longitude = MISSING
                        store_number = MISSING
                        log.info(
                            "Append {} => {}".format(location_name, street_address)
                        )
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=LOCATION_URL,
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
                else:
                    raw_address = ", ".join(info[1:]).strip()
                    street_address, city, state, zip_postal, country_code = getAddress(
                        raw_address
                    )
                    if country_code == MISSING:
                        country_code = "US"
                    hours_of_operation = MISSING
                    latitude = MISSING
                    longitude = MISSING
                    store_number = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
