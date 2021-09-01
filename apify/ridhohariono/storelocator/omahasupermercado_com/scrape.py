from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "omahasupermercado.com"
BASE_URL = "https://www.omahasupermercado.com"
LOCATION_URL = "https://www.omahasupermercado.com/"
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field.strip()


def get_latlong(gmap_url):
    try:
        pattern = r"(-?[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)"
        latlong = re.search(pattern, gmap_url)
    except:
        return MISSING, MISSING
    return latlong.group(2), latlong.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_urls = soup.find("li", {"id": "menu-item-170"}).find("ul").find_all("a")
    for row in store_urls:
        page_url = row["href"]
        soup = pull_content(page_url)
        content = (
            soup.find("section", {"class": "av_textblock_section"})
            .get_text(strip=True, separator=",")
            .replace("Our Store:,", "")
            .replace("Phone:,", "")
            .replace("Hours:,", "")
        ).split(",")
        location_name = soup.find(
            "h1", {"class": "av-special-heading-tag"}
        ).text.strip()
        street_address = content[0].strip()
        city = content[1].strip()
        state = content[2].split()[0].strip()
        zip_code = content[2].split()[1].strip()
        phone = content[3].strip()
        hours_of_operation = " ".join(content[4:]).strip()
        store_number = MISSING
        country_code = "US"
        location_type = "omahasupermercado"
        latitude, longitude = get_latlong(soup.find("iframe")["src"])
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_code.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address}, {city}, {state} {zip_code} ",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
