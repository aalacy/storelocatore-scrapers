from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "spar.no"
BASE_URL = "https://spar.no/finn-butikk/"
API_URL = "https://api.ngdata.no/sylinder/stores/v1/basic-info?chainId=1210"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        info = row["storeDetails"]
        page_url = BASE_URL + info["slug"]
        store = pull_content(page_url)
        location_name = info["storeName"]
        street_address = (
            info["organization"]["address"]
            if info["organization"]["address"]
            else MISSING
        )
        city = info["organization"]["city"] if info["organization"]["city"] else MISSING
        if city.lower() == street_address.lower():
            street_address == MISSING
        state = info["county"]
        zip_postal = (
            info["organization"]["postalCode"]
            if info["organization"]["postalCode"]
            else MISSING
        )
        country_code = "NO"
        phone = info["organization"]["phone"]
        store_number = info["storeId"]
        hours_of_operation = (
            re.sub(
                r"(\D),",
                r"\1:",
                re.sub(
                    r"\s?\(.*\)\s?",
                    r"",
                    store.find(
                        "dl", {"class": "openinghours openinghours--ordinary"}
                    ).get_text(strip=True, separator=", "),
                ).strip(),
            )
            .replace("Stengt:", "Stengt,")
            .strip()
        )
        location_type = MISSING
        latitude = info["position"]["lat"]
        longitude = info["position"]["lng"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
