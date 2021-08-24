from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
import re


session = SgRequests()
website = "ritecheck_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://ritecheck.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        search_url = "https://ritecheck.com/locations.html"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.find("ul", {"class": "locations-list"}).findAll("li")
        for loc in locations:
            addresses = loc.find("p", {"class": "locations-list-title"}).findAll("a")
            hours = loc.findAll("p")[1].text
            for addr in addresses:
                address = addr.text
                hours = hours
                hours = hours.replace("â", "-")
                address = re.sub(pattern, " ", address)
                address = re.sub(cleanr, " ", address)

                hours = hours.replace(",", "")
                hours = hours.strip()

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=DOMAIN,
                    location_name=MISSING,
                    street_address=MISSING,
                    city=MISSING,
                    state=MISSING,
                    zip_postal=MISSING,
                    country_code=MISSING,
                    store_number=MISSING,
                    phone=MISSING,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours.strip(),
                    raw_address=address.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
