import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "spar.al"
BASE_URL = "https://www.spar.al"
LOCATION_URL = "https://www.spar.al/index.php/al/spar-harta"
HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("script", string=re.compile("phocaMapPlgPM1.*"))
    data = re.findall(r"content:\s+'(.*)'", content.string)
    dropdown = soup.find("select", id="toPMAddressPlgPM1").find_all("option")
    for i in range(len(dropdown)):
        info = bs(data[i], "lxml").get_text(strip=True, separator=",")
        raw_address = re.sub(r",GPS.*", "", info)
        phone = re.search(r",Tel:(.*)", raw_address)
        try:
            phone = phone.group(1).strip()
            raw_address = re.sub(r",Tel:.*", "", raw_address)
        except:
            phone = "355689000114"
        raw_address = raw_address.replace('"', "")
        location_name = dropdown[i].text.replace('"', "").strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        if street_address == MISSING:
            street_address, city, state, zip_postal = getAddress(location_name)
        store_number = MISSING
        location_type = MISSING
        hours_of_operation = MISSING
        country_code = "AL"
        latlong = dropdown[i]["value"].split(",")
        latitude = latlong[0]
        longitude = latlong[1]
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
                    SgRecord.Headers.LOCATION_NAME,
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
