from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "shoppersstop.com"
BASE_URL = "https://www.shoppersstop.com"
LOCATION_URL = "https://www.shoppersstop.com/store-finder"
API_URL = "https://www.shoppersstop.com/store-finder?q={}&page={}"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    city_name = soup.find("select", id="city-name").find_all("option")
    for city in city_name:
        num = 0
        url = API_URL.format(city["value"], num)
        data = session.get(url, headers=HEADERS).json()
        log.info("Get location from " + url)
        for row in data["results"]:
            page_url = (
                BASE_URL
                + "/storecode/"
                + row["code"]
                + "/"
                + row["displayName"].replace(" ", "_")
            )
            location_name = row["displayName"]
            if row["address"]["line2"]:
                street_address = (
                    row["address"]["line1"] + " " + row["address"]["line2"].strip()
                )
            else:
                street_address = row["address"]["line1"].strip()
            city = row["address"]["town"]
            state = (
                MISSING
                if not row["address"]["region"]
                else row["address"]["region"]["name"]
            )
            zip_postal = row["address"]["postalCode"]
            phone = row["address"]["phone"]
            country_code = (
                "IN"
                if not row["address"]["country"]
                else row["address"]["country"]["isocode"]
            )
            if not row["openingHours"]:
                hours_of_operation = MISSING
            else:
                hoo = ""
                for hday in row["openingHours"]["weekDayOpeningList"]:
                    day = hday["weekDay"]
                    hours = (
                        "Closed"
                        if hday["closed"]
                        else hday["openingTime"]["formattedHour"]
                        + "-"
                        + hday["closingTime"]["formattedHour"]
                    )
                    hoo += day + ": " + hours + ","
                hours_of_operation = hoo.rstrip(",")
            location_type = row["type"]
            store_number = row["code"]
            latitude = (
                MISSING
                if row["geoPoint"]["latitude"] == 0.0
                else row["geoPoint"]["latitude"]
            )
            longitude = (
                MISSING
                if row["geoPoint"]["longitude"] == 0.0
                else row["geoPoint"]["longitude"]
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
            num += 1


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
