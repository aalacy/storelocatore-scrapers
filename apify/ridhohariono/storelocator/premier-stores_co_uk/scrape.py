import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "premier-stores_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

LOCATION_URL = "https://www.premier-stores.co.uk/sitemap.xml"
DOMAIN = "https://www.premier-stores.co.uk/"
MISSING = SgRecord.MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=headers)
    if req.status_code == 500:
        return False
    soup = bs(req.content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return MISSING
    return field


def parse_hours(table):
    if not table:
        return MISSING
    hoo = table.get_text(strip=True, separator=",").replace("day:,", "day: ")
    return hoo.replace("Day,Open,closed,", "")


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def find_meta(soup, query):
    el = soup.find("meta", query)
    if not el:
        return MISSING
    return handle_missing(soup.find("meta", query)["content"])


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    for val in soup.find_all("loc", text=re.compile(r"\/sitemap\.xml\?page\=\d+")):
        page = pull_content(val.text)
        for row in page.find_all("loc", text=re.compile(r"\/our-stores\/\D+")):
            if (
                not re.match(r".*\-0$", row.text)
                and "/woodside-convenience-store-2" not in row.text
            ):
                store_urls.append(row.text)
    store_urls = list(set(store_urls))
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    for page_url in store_urls:
        soup = pull_content(page_url)
        if not soup:
            continue
        location_name = find_meta(soup, {"name": "geo.placename"})
        street_address = handle_missing(
            find_meta(soup, {"property": "og:street_address"}).strip(",").strip()
        )
        except_url = ["windmill-hill", "four-lane-stores"]
        if page_url not in except_url:
            street_address = re.sub(r",$", "", street_address).strip().split(",")
            street_address = street_address[0].strip()
        city = find_meta(soup, {"property": "og:locality"})
        zip_postal = find_meta(soup, {"property": "og:postal_code"})
        state = find_meta(soup, {"property": "og:region"})
        country_code = "GB"
        store_number = MISSING
        phone = find_meta(soup, {"property": "og:phone_number"})
        hours_of_operation = parse_hours(
            soup.find("div", {"id": "storeOpeningTimes"}).find("table")
        )
        location_type = find_meta(soup, {"property": "og:type"})
        latitude = find_meta(soup, {"property": "latitude"})
        longitude = find_meta(soup, {"property": "longitude"})
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
