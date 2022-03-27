import ssl
import json
from sglogging import sglog
from sgselenium import SgChrome
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


session = SgRequests()
website = "basechildrenswear_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.basechildrenswear.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        with SgChrome(
            executable_path=ChromeDriverManager().install(), is_headless=True
        ) as driver:
            url = "https://www.basechildrenswear.com/store-locator/all-stores/"
            driver.get(url)
            response_text = driver.page_source
            soup = BeautifulSoup(response_text, "html.parser")
            loclist = soup.findAll("li", {"data-e2e": "storeLocator-list-item"})
            for loc in loclist:
                page_url = DOMAIN + loc.find("a")["href"]
                log.info(page_url)
                driver.get(page_url)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                schema = driver.page_source.split(
                    '<script type="application/ld+json">'
                )[1].split("</script>", 1)[0]
                schema = schema.replace("\n", "")
                loc = json.loads(schema)
                location_name = loc["name"]
                address = loc["address"]
                phone = loc["telephone"]
                street_address1 = driver.page_source.split('"address1": "')[1].split(
                    '"'
                )[0]
                street_address2 = driver.page_source.split('"address2": "')[1].split(
                    '"'
                )[0]
                street_address = street_address1 + " " + street_address2
                street_address = street_address.replace("- Store Now Closed", "").strip(
                    ","
                )
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                phone = loc["telephone"]
                hour_list = loc["openingHoursSpecification"]
                latitude = loc["geo"]["latitude"]
                longitude = loc["geo"]["longitude"]
                hours_of_operation = (
                    soup.find("div", {"id": "storeTimes"})
                    .find("p")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Normal Opening hours", "")
                )
                country_code = "UK"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
