import ssl
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
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
website = "joecoffeecompany_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://joecoffeecompany.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://joecoffeecompany.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "list-unstyled"}).findAll("li")
        with SgChrome(executable_path=ChromeDriverManager().install()) as driver:
            for loc in loclist:
                page_url = DOMAIN + loc.find("a")["href"]
                log.info(page_url)
                driver.get(page_url)
                if "Now Closed" in driver.page_source:
                    continue
                soup = BeautifulSoup(driver.page_source, "html.parser")
                location_name = soup.find("h1").text
                try:
                    street_address = (
                        soup.find("span", {"data-yext-field": "address1"}).text
                        + " "
                        + soup.find("span", {"data-yext-field": "address2"}).text
                    )
                except:
                    street_address = soup.find(
                        "span", {"data-yext-field": "address2"}
                    ).text
                city = soup.find("span", {"data-yext-field": "city"}).text
                state = soup.find("span", {"data-yext-field": "state"}).text
                zip_postal = soup.find("span", {"data-yext-field": "zip"}).text
                phone = MISSING
                country_code = "US"
                hours_of_operation = (
                    soup.find("div", {"data-yext-field": "hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                try:
                    coords = str(soup).split("/@")[1].split(",")
                    latitude = coords[0]
                    longitude = coords[1]
                except:
                    latitude = MISSING
                    longitude = MISSING
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
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
