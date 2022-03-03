from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "spaviadayspa.com"
LOCATION_URL = "https://spaviadayspa.com/location"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(page_url):
    url = page_url + "/about-us"
    soup = pull_content(url)
    hoo = (
        soup.find("strong", text="Hours of Operation")
        .find_next("p")
        .get_text(strip=True, separator=",")
    ).strip()
    return hoo


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    states_link = soup.find("select", id="state-dropdown").find_all(
        "option", {"value": re.compile(r"\/service.*")}
    )
    for val in states_link:
        keyword = val["value"].split("?st=")[1]
        api_url = f"https://spaviadayspa.com/service/directorylisting/filterMarkers?s={keyword}"
        data = session.get(api_url, headers=HEADERS).json()
        for row in data["markers"]:
            page_url = row["web_site"]
            location_name = row["name"]
            if row["address2"]:
                street_address = (row["address1"] + " " + row["address2"]).strip()
            else:
                street_address = row["address1"]
            city = row["city"]
            state = row["state"]
            zip_postal = row["zip"]
            phone = row["phone"]
            country_code = row["country"]
            store_number = row["id"]
            hours_of_operation = get_hoo(page_url)
            latitude = row["lat"]
            longitude = row["lon"]
            location_type = MISSING
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
