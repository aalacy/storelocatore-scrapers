from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import urllib
import re

DOMAIN = "bn.com.pe"
LOCATION_URL = "https://www.bn.com.pe/canales-atencion/agentes-lima-metropolitana.asp"
STORE_URL = "https://www.bn.com.pe/canales-atencion/base-datos/agentes-lima-metropolitana.asp?distrito={}"
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "charset=utf-8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": LOCATION_URL,
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    districts = soup.select("select#distrito option")
    phone = (
        soup.find("span", {"class": "portal"})
        .text.replace("Línea telefónica:", "")
        .split("/")[0]
        .strip()
    )
    for district in districts:
        city = district["value"]
        page_url = STORE_URL.format(urllib.parse.quote_plus(city))
        content = pull_content(page_url)
        location_type = content.find("ul").attrs["class"][0].title()
        stores = content.select("ul li")
        for row in stores:
            location_name = (
                row.find("div", {"class": "nombre-oficina"})
                .text.replace("\n", "")
                .strip()
            )
            addr = re.sub(
                r"\(.*\)",
                "",
                row.find_all("div", {"class": "direccion"})[1]
                .text.replace("Dirección: ", "")
                .strip(),
            )
            street_address, _, _, _ = getAddress(addr)
            zip_postal = MISSING
            state = row.find("div", {"class": "titulo-departamento"}).text.strip()
            country_code = "PE"
            hours_of_operation = MISSING
            store_number = MISSING
            latitude = MISSING
            longitude = MISSING
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
                raw_address=addr,
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
