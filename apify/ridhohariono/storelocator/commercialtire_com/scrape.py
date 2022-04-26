from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgSelenium
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "commercialtire.com"
BASE_URL = "https://commercialtire.com"
LOCATION_URL = "https://www.commercialtire.com/locations"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
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
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    soup = bs(driver.page_source, "lxml")
    contents = soup.find("div", {"id": "1968833344"}).find_all(
        "a", {"data-display-type": "block"}
    )
    for row in contents:
        page_url = BASE_URL + row["href"]
        content = pull_content(page_url)
        info = content.find(
            "div",
            {"class": re.compile(r"u_(.*) dmRespRow fullBleedChanged fullBleedMode")},
        )
        if not info:
            driver.get(page_url)
            content = bs(driver.page_source, "lxml")
            info = content.find(
                "div",
                {
                    "class": re.compile(
                        r"u_(.*) dmRespRow fullBleedChanged fullBleedMode"
                    )
                },
            )
        location_name = row.text.strip()
        addr_info = info.find("div", {"data-type": "inlineMap"})
        raw_address = addr_info["data-address"].strip()
        if "boise---state" in page_url:
            raw_address = "1190 W State St, Downtown Boise, Boise, ID, United States"
        street_address, city, state, zip_postal = getAddress(raw_address)
        street_address = street_address.replace("Winstead Park", "").replace(
            "Yakima", ""
        )
        store_number = MISSING
        phone_content = info.find(
            re.compile(r"p|span"),
            {
                "class": re.compile(
                    r"m-font-size-19 font-size-24|m-size-17 size-24|font-size-24 m-font-size-19"
                )
            },
        )
        try:
            phone = phone_content.text.replace("\n", "").strip()
        except:
            phone = MISSING
        country_code = "US"
        location_type = "commercialtire"
        addr_info = info.find("div", {"data-type": "inlineMap"})
        latitude = addr_info["data-lat"]
        longitude = addr_info["data-lng"]
        hours_of_operation = ", ".join(
            info.find("span", text="HOURS:")
            .find_parent("div")
            .get_text(strip=True, separator="@")
            .split("@")[3:]
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
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
