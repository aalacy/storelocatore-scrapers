import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import json

DOMAIN = "kbane.com"
BASE_URL = "https://www.kbane.com"
LOCATION_URL = "https://www.kbane.com/showrooms"
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def singleQuoteToDoubleQuote(singleQuoted):
    cList = list(singleQuoted)
    inDouble = False
    inSingle = False
    for i, c in enumerate(cList):
        if c == "'":
            if not inDouble:
                inSingle = not inSingle
                cList[i] = '"'
        elif c == '"':
            inDouble = not inDouble
    doubleQuoted = "".join(cList)
    return doubleQuoted


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = singleQuoteToDoubleQuote(
        re.search(
            r"Data_ShowroomsListe\.datas\.showrooms = (\[.*\]);",
            soup.find(
                "script", string=re.compile(r"Data_ShowroomsListe\.datas\.showrooms")
            ).string,
        )
        .group(1)
        .replace('"', "'")
        .replace(",}", "}")
    )
    data = json.loads(contents)
    for row in data:
        page_url = row["url"]
        store = pull_content(page_url)
        location_name = row["title"].replace('"', "'").strip()
        raw_address = row["adresse"].replace("<br/>", ", ").replace('"', "'").strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "FR"
        try:
            phone = (
                store.find("div", {"class": "b_tel b-a_tel"})
                .text.replace("Tél :", "")
                .strip()
            )

        except:
            phone = MISSING
        try:
            hours_of_operation = re.sub(
                r"Samedi:$",
                "Samedi: Fermé",
                store.find("div", {"class": "b-h_horaires"})
                .get_text(strip=True, separator=",")
                .replace("di", "di: ")
                .replace(": ,", ": ")
                .strip(),
            )
        except:
            hours_of_operation = MISSING
        if row["type"] == "showroom":
            location_type = "SHOWROOM"
        else:
            location_type = "DEPOT/AGENCIES"
        store_number = MISSING
        latitude = row["latitude"]
        longitude = row["longitude"]
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
