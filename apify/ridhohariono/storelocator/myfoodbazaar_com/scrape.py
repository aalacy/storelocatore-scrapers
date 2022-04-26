from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json


DOMAIN = "myfoodbazaar.com"
BASE_URL = "https://www.myfoodbazaar.com/"
LOCATION_URL = "https://www.foodbazaar.com/find-your-store/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(r"var\s+" + js_variable + r".*", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"(?s)var\s+" + js_variable + r"\s+=\s+\[(\{.*?\})\]", info)
    data = json.loads("[{}]".format(parse.group(1)))
    return data


def fetch_data():
    store_info = parse_json(LOCATION_URL, "locations")
    for row in store_info:
        if row["circularGroupName"] == "Coming Soon":
            continue
        location_name = row["name"]
        if "address2" in row:
            street_address = "{}, {}".format(row["address1"], row["address2"])
        else:
            street_address = row["address1"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["zipCode"]
        country_code = "US"
        store_number = row["storeNumber"]
        try:
            phone = row["phone"]
        except:
            phone = MISSING
        location_type = MISSING
        latitude = row["latitude"]
        longitude = row["longitude"]
        hours_of_operation = row["hourInfo"].replace("7 Days a Week: ", "")
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
