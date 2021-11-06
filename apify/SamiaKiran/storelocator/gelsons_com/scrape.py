import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

session = SgRequests()
website = "gelsons_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.gelsons.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        with SgChrome(executable_path="C:/webdrivers/chromedriver.exe") as driver:
            url = "https://www.gelsons.com/stores"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            loclist = soup.find("ol").findAll("li")
        for loc in loclist:
            temp = loc.findAll("div")
            page_url = DOMAIN + temp[3].find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = (
                soup.findAll("a", {"rel": "noreferrer"})[1]
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            city = address[1]
            state = address[2].replace(",", "")
            zip_postal = address[3]
            loc = json.loads(r.text.split('"store":')[1].split(',"layoutProps"')[0])
            location_name = loc["title"]
            phone = loc["storePhone"]
            latitude = loc["lat"]
            longitude = loc["long"]
            country_code = "US"
            hours_of_operation = soup.find(
                "h2", {"class": "font-bold flex text-2xl pb-5"}
            ).text.replace("Hours:", "")
            country_code = "US"
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
