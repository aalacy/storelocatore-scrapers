from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

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
    days = [
        {"label": "Su", "name": "Sunday:"},
        {"label": "Mo", "name": "Monday:"},
        {"label": "Tu", "name": "Tuesday:"},
        {"label": "We", "name": "Wednesday:"},
        {"label": "Th", "name": "Thursday:"},
        {"label": "Fr", "name": "Friday:"},
        {"label": "Sa", "name": "Saturday:"},
    ]
    for link in links:
        soup = pull_content(link)
        data = json.loads(
            soup.find("script", id="popmenu-apollo-state")
            .string.replace("window.POPMENU_APOLLO_STATE = ", "")
            .replace("};", "}")
            .replace('" + "', "")
            .strip()
        )
        for key, value in data.items():
            if key.startswith("RestaurantLocation:"):
                if (
                    "customLocationContent" in value
                    and "Coming Soon!" in value["customLocationContent"]
                ):
                    continue
                try:
                    page_url = BASE_URL + value["slug"]
                    location_name = value["name"]
                    raw_address = value["fullAddress"].replace("\n", ", ").strip()
                    city = value["city"]
                    state = value["state"]
                    zip_postal = value["postalCode"]
                    street_address = (
                        value["streetAddress"]
                        .replace("\n", ", ")
                        .replace("Level 1 Pullman Paris Montparnasse Hotel", "")
                        .strip()
                    )
                except:
                    continue
                country_code = value["country"]
                phone = value["displayPhone"]
                location_type = MISSING
                store_number = value["id"]
                latitude = value["lat"]
                longitude = value["lng"]
                hoo = ""
                try:
                    for day in days:
                        day_available = False
                        for hday in value["schemaHours"]:
                            if day["label"] in hday:
                                day_available = True
                                hoo += hday.replace(day["label"], day["name"]) + ","
                        if not day_available:
                            hoo += day["name"] + " Closed" + ","
                        hoo = hoo.replace(
                            day["name"]
                            + " 16:30-19:00,"
                            + day["name"]
                            + " 11:30-15:00",
                            day["name"]
                            + " 11:30-15:00,"
                            + day["name"]
                            + " 16:30-19:00",
                        )
                except:
                    pass
                hours_of_operation = hoo.strip().rstrip(",")
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
