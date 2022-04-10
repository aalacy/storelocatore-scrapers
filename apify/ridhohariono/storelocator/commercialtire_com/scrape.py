from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "commercialtire.com"
BASE_URL = "https://commercialtire.com"
LOCATION_URL = "https://www.commercialtire.com/locations"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
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
    soup = pull_content(LOCATION_URL)
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
        try:
            phone = info.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
            if len(phone) < 2:
                phone = info.find(
                    "a",
                    {
                        "href": re.compile(r"tel:.*"),
                        "class": "font-size-24 m-font-size-17",
                    },
                ).text.strip()
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
