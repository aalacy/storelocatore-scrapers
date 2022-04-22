import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "wienerschnitzel_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://wienerschnitzel.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.wienerschnitzel.com/locations-all/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "results_entry"})
    for loc in loclist:
        if re.match(r"^http", loc.find("a")["href"]):
            page_url = loc.find("a")["href"]
        else:
            page_url = "https://www.wienerschnitzel.com" + loc.find("a")["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        street_address = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
        country_code = "US"

        hours_of_operation = (
            soup.find("div", {"class": "location-hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Dining room closes at 11pm", "")
        )
        location_type = MISSING
        if "Coming - - Soon" in hours_of_operation:
            hours_of_operation = MISSING
            location_type = "Coming Soon"
        location_name = (
            soup.find("h1").get_text(separator="|", strip=True).replace("|", " ")
        )
        try:
            phone = soup.find("span", {"itemprop": "telephone"}).text
        except:
            phone = "<MISSING>"
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
            location_type=location_type,
            latitude=MISSING,
            longitude=MISSING,
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
