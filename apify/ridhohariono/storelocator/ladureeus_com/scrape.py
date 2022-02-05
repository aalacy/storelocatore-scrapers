from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "laduree.com"
BASE_URL = "https://www.laduree.us"
LOCATION_URL = "https://www.laduree.us/locations"
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


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", {"class": "content-left"})
    try:
        hoo_content.find("div", {"class": "post-thumb"}).decompose()
        hoo_content.find("p", {"style": "text-align: center;"}).decompose()
        hoo_content.find("h3").decompose()
    except:
        pass
    for content in hoo_content.find_all("p"):
        if re.match(r"Store Hours", content.text.strip(), re.IGNORECASE):
            content.decompose()
            break
        content.decompose()
    hours_of_operation = (
        re.sub(
            r",Holiday Hours.*",
            "",
            ",".join([hoo.text.strip() for hoo in hoo_content.find_all("p")]).strip(),
            re.IGNORECASE,
        )
        .strip()
        .rstrip(",")
    )
    return hours_of_operation


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("div", {"class": "col sqs-col-12 span-12"}).select(
        "div.sqs-block.html-block.sqs-block-html"
    )[1:]
    for row in contents:
        location_name = row.find("h3").get_text(strip=True, separator=" ").upper()
        row.find("h3").decompose()
        info = re.sub(
            r"\|\|[\w.+-]+@[\w-]+\.[\w.-]+",
            "",
            row.get_text(strip=True, separator="||"),
        )
        info = re.sub(r"\|\|Opening Hours:?\|\|", "HOURS", info)
        addr = info.split("HOURS")[0].split("||")
        if len(addr) > 1:
            raw_address = ", ".join(addr[:-1])
            phone = addr[-1]
        else:
            raw_address = addr[0].strip()
            phone = MISSING
            hours_of_operation = MISSING
        hours_of_operation = info.split("HOURS")[-1].replace("||", ",")
        raw_address = (
            raw_address.replace("D.C.", "DC")
            .replace("-", ",")
            .replace(", USA", "")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            try:
                zip_postal = re.search(r"(\d{5})", raw_address).group(1)
                street_address = re.sub(
                    zip_postal + r",?\s?", "", street_address
                ).strip()
            except:
                zip_postal = MISSING
        country_code = "US"
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
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
