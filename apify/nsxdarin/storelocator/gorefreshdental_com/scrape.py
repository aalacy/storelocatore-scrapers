from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

DOMAIN = "gorefreshdental.com"
BASE_URL = "https://gorefreshdental.com"
LOCATION_URL = "https://gorefreshdental.com/locations"
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
    contents = soup.select("div.coh-wysiwyg a")
    for row in contents:
        if DOMAIN not in row["href"]:
            page_url = BASE_URL + row["href"]
        else:
            page_url = row["href"]
        store = pull_content(page_url)
        location_name = row.text.strip()
        try:
            street = (
                store.find("span", {"class": "address-line1"}).text
                + " "
                + store.find("span", {"class": "address-line2"}).text
            ).strip()
        except:
            street = store.find("span", {"class": "address-line1"}).text.strip()
        street_address = street.strip().rstrip(".")
        city = store.find("span", {"class": "locality"}).text.strip()
        state = store.find("span", {"class": "administrative-area"}).text.strip()
        zip_postal = store.find("span", {"class": "postal-code"}).text.strip()
        country = store.find("span", {"class": "country"}).text.strip()
        country_code = "US" if country == "United States" else country
        phone = store.find(
            "div", {"class": "coh-container location_data__phone coh-ce-f66a5634"}
        ).text.strip()
        try:
            hours_of_operation = (
                store.find("div", {"class": "office-hours"})
                .get_text(strip=True, separator=",")
                .replace(":,", ": ")
            )
        except:
            hours_of_operation = MISSING
        location_type = MISSING
        if "Temporarily Closed" in row.parent.text.strip():
            location_type = "Temporarily Closed"
        latlong = list(
            json.loads(
                store.find(
                    "script", {"data-drupal-selector": "drupal-settings-json"}
                ).string
            )["leaflet"].values()
        )[0]["features"][0]
        store_number = MISSING
        latitude = latlong["lat"]
        longitude = latlong["lon"]
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
