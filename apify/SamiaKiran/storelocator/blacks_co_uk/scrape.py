import ssl
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


ssl._create_default_https_context = ssl._create_unverified_context

session = SgRequests()
website = "blacks_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://blacks.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.blacks.co.uk/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=stores]")
        loclist = loclist
        for loc in loclist:
            location_name = loc.text
            page_url = "https://www.blacks.co.uk" + loc["href"]
            log.info(page_url)
            with SgChrome() as driver:
                driver.get(page_url)
                response_text = driver.page_source
                soup = BeautifulSoup(response_text, "html.parser")
                try:
                    street_address = (
                        soup.find("span", {"data-yext-field": "address1"}).text
                        + " "
                        + soup.find("span", {"data-yext-field": "address2"}).text
                    )
                except:
                    street_address = soup.find(
                        "span", {"data-yext-field": "address1"}
                    ).text
                city = soup.find("span", {"data-yext-field": "city"}).text
                state = soup.find("span", {"data-yext-field": "state"}).text
                zip_postal = soup.find("span", {"data-yext-field": "zip"}).text
                country_code = "UK"
                phone = soup.find("a", {"data-yext-field": "phone"}).text
                hours_of_operation = (
                    soup.find("ul", {"id": "opening_times"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                latitude = str(soup).split('"latitude":')[1].split(",")[0]
                longitude = str(soup).split('"longitude":')[1].split(",")[0]
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
