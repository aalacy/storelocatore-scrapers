from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "umamiburger.com"
BASE_URL = "https://www.umamiburger.com/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    links = [
        "https://www.umamiburger.com/dine-in-locations",
        "https://www.umamiburger.com/pick-up-and-delivery",
    ]
    for link in links:
        soup = pull_content(link)
        soupstr = str(soup.find("script", id="popmenu-apollo-state"))
        items = soupstr.split('"RestaurantLocation:')
        for item in items:
            if "Coming Soon!" not in item and "POPMENU_" not in item:
                try:
                    page_url = BASE_URL + item.split('"slug":"')[1].split('"')[0]
                    location_name = item.split('"name":"')[1].split('"')[0]
                    raw_address = (
                        item.split('"fullAddress":"')[1]
                        .split('"')[0]
                        .replace("\n", ", ")
                        .strip()
                    )
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zip_postal = item.split('"postalCode":"')[1].split('"')[0]
                    street_address = (
                        item.split('"streetAddress":"')[1]
                        .split('"')[0]
                        .replace("\n", ", ")
                        .replace("Level 1 Pullman Paris Montparnasse Hotel,", "")
                        .strip()
                    )
                except:
                    continue
                country_code = item.split('"country":"')[1].split('"')[0]
                try:
                    phone = item.split('"displayPhone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                location_type = MISSING
                store_number = item.split('"id":')[1].split(",")[0]
                latitude = item.split('"lat":')[1].split(",")[0]
                longitude = item.split('"lng":')[1].split(",")[0]
                hoo = ""
                try:
                    hoo = (
                        item.split('"schemaHours":["')[1]
                        .split('],"show')[0]
                        .replace('","', "; ")
                        .replace('"', "")
                    )
                except:
                    pass
                hours_of_operation = hoo.strip()
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
                    raw_address=raw_address,
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
