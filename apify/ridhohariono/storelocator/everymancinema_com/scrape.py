from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json

DOMAIN = "everymancinema.com"
BASE_URL = "https://www.everymancinema.com/"
LOCATION_URL = "https://www.everymancinema.com/venues-list"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("script", string=re.compile(r"pc\.venuesList.*"))
    data = json.loads(
        re.sub(
            r",$",
            "",
            re.search(r"current:\s+(.*)", content.string)
            .group(1)
            .strip()
            .replace("\\'", "")
            .replace("comingSoon", '"comingSoon"'),
        )
    )
    for row in data:
        page_url = BASE_URL + row["UrlFriendlyName"]
        location_name = row["Name"]
        street_address = ""
        if row["Cinema"]["Address1"]:
            street_address += row["Cinema"]["Address1"]
        if row["Cinema"]["Address2"]:
            street_address += row["Cinema"]["Address2"]
        city = row["Cinema"]["City"]
        state = row["Cinema"]["StateName"]
        zip_postal = row["Cinema"]["ZipCode"]
        country_code = "UK"
        phone = re.findall(
            r"\d{4}\s+\d{3}\s+\d{4}|\d{5}\s+\d{6}", row["Cinema"]["Phone"]
        )[-1]
        store_number = row["CinemaId"]
        location_type = "Cinema"
        latitude = row["Cinema"]["Latitude"]
        longitude = row["Cinema"]["Longitude"]
        hours_of_operation = (
            row["Cinema"]["CinemaInfo"]["OpeningTimes"]
            .replace(
                "(or half an hour before the first film of the day, if earlier)", ""
            )
            .replace(".", "")
            .strip()
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
