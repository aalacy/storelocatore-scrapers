from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import re

DOMAIN = "theeyedoctors.net"
LOCATION_URL = "https://www.theeyedoctors.net/locations/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


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
    data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    for row in data["props"]["pageProps"]["locations"]:
        page_url = LOCATION_URL + row["slug"]
        content = pull_content(page_url)
        location_name = row["name"]
        street_address = (row["address1"] + " " + row["address2"]).strip()
        city = row["city"]
        state = row["state"]
        zip_postal = row["zipCode"]
        street_address = re.sub(
            r",$",
            "",
            street_address.replace(city, "")
            .replace(state, "")
            .replace(zip_postal, "")
            .strip(),
        )
        phone = row["phoneNumber"]
        country_code = "US"
        location_type = MISSING
        store_number = MISSING
        hoo_content = content.find("div", {"class": "w-full md:w-1/2 mt-5"})
        try:
            hoo_content.find("h2").decompose()
            hoo_content.find(
                "div", {"class": "w-full md:w-2/3 mt-6 mb-6 text-red"}
            ).decompose()
            hoo_content.find(
                "span", {"class": "mt-3 block italic text-center font-medium"}
            ).decompose()
        except:
            pass
        hours_of_operation = (
            hoo_content.get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace("Schedule Your Eye Exam", "")
        ).rstrip(",")
        latitude = row["map"]["lat"]
        longitude = row["map"]["lon"]
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
