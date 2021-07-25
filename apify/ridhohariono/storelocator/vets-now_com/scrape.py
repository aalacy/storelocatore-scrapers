import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


DOMAIN = "vets-now.com"
BASE_URL = "https://www.vets-now.com"
LOCATION_URL = "https://www.vets-now.com/clinics-sitemap.xml"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = [
        val.text
        for val in soup.find_all(
            "loc", text=re.compile(r"\/find-an-emergency-vet\/\D+")
        )
    ]
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    for page_url in store_urls:
        soup = pull_content(page_url)
        info = parse_json(soup)["@graph"][5]
        if "name" not in info:
            info = parse_json(soup)["@graph"][6]
        location_name = handle_missing(info["name"])
        address = info["address"].replace(",,", ",")
        address = re.sub(r"<br.*", "", address)
        address = re.sub(r",$", "", address.strip()).split(",")
        del address[0]
        if len(address) > 2:
            if len(address) > 4:
                street_address = ", ".join(address[:-3]).strip()
                city = address[-3].strip()
            else:
                street_address = ", ".join(address[:-2]).strip()
                city = address[-2].strip()
            if "United Kingdom" in city:
                city = location_name.replace("Vets Now ", "").strip()
        else:
            street_address = address[0].strip()
            city = re.sub(
                r"[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}", "", address[1]
            ).strip()
        state = "<MISSING>"
        zip_code = handle_missing(
            re.findall(
                r"[A-Z]{1,2}[0-9A-Z]{1,2}[0-9A-Z]? [0-9][A-Z]{2}",
                ",".join(address).strip(),
            )[0]
        )
        country_code = "GB"
        store_number = "<MISSING>"
        phone = handle_missing(info["telephone"])
        hoo_content = soup.find("ul", {"id": "clinic__opens"})
        if not hoo_content:
            hoo_content = soup.find("table", {"class": "clinic-times"}).find("tbody")
        hours_of_operation = (
            hoo_content.get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(",–,", " - ")
            .replace("Open,24h", "24 Hours")
            .replace(",from,", " from ")
            .strip()
        )
        location_type = "<MISSING>"
        latitude = handle_missing(info["geo"]["latitude"])
        longitude = handle_missing(info["geo"]["longitude"])
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
