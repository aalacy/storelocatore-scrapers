from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


DOMAIN = "chaussurespop.com"
BASE_URL = "https://www.chaussurespop.com"
LOCATION_URL = "https://www.chaussurespop.com/pages/trouver-un-magasin"
API_URL = "https://sheets.googleapis.com/v4/spreadsheets/1PApiFhykfKLXF8diWTvcJzNh2YK6fmu9CJDljKZSr_A/values/Feuille%201?key="
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "origin": BASE_URL,
    "referer": BASE_URL,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_token():
    soup = pull_content(LOCATION_URL)
    token = soup.find("div", {"class": "store_map"})["data-api-key"]
    return token


def fetch_data():
    log.info("Fetching store_locator data")
    token = get_token()
    data = session.get(API_URL + token, headers=HEADERS).json()
    for row in data["values"][1:]:
        location_name = row[0]
        street_address = row[1]
        city = row[2]
        state = row[3]
        zip_postal = row[5]
        country_code = "CA" if row[4] == "CANADA" else row[4]
        phone = row[6]
        if len(row) <= 10:
            hours_of_operation = MISSING
        else:
            hours_of_operation = row[10].replace("  ", ": ").replace("\n", "").strip()
        store_number = MISSING
        location_type = MISSING
        latitude = row[7]
        longitude = row[8]
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
