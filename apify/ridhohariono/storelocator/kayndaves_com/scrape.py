from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re


DOMAIN = "kayndaves.com"
BASE_URL = "https://www.kayndaves.com"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = soup.select("div#Containerc1dmp div._2Hij5")[-3:-1]
    for row in contents:
        location_name = row.find("h6").text.replace("\u200b", "").strip()
        addr = row.find("a", {"href": re.compile(r"\/maps\/place.*")})
        street_address = addr.text.strip()
        if "city" in location_name:
            city = location_name.replace("city", "")
        else:
            city = MISSING
        state = MISSING
        zip_postal = MISSING
        phone = row.find("a", {"href": re.compile(r"tel.*")}).text.strip()
        country_code = "US"
        hoo_content = (
            row.get_text(strip=True, separator=",")
            .replace("\u200b", "")
            .strip(",")
            .split(",")
        )
        hoo = ",".join(hoo_content[3:])
        if "reopening" in hoo:
            location_type = "TEMP_CLOSED"
            hours_of_operation = MISSING
        else:
            location_type = MISSING
            hours_of_operation = (
                re.sub(r"- HOURS -|>>>.*|- TEMPORARY HOURS -,?", "", hoo)
                .strip(",")
                .replace("  ==  ", ",")
                .strip()
            )
        store_number = MISSING
        latitude, longitude = get_latlong(addr["href"])
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=BASE_URL,
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
