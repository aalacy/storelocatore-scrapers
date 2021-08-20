import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "worldwidestereo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://www.worldwidestereo.com/pages/showrooms"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.find(
        "div", {"class": "callout-grid__row grid grid--2-at-medium"}
    ).find_all("div", {"class": "callout-grid__column grid__cell"})
    for div in divs:
        page_url = div.find("a").get("href")
        log.info(page_url)
        r = session.get(page_url)
        soup = BeautifulSoup(r.text, "html.parser")
        data = soup.find(
            "div", {"class": "callout-grid__row grid grid--3-at-medium"}
        ).find_all("div", {"class": "callout-grid__column grid__cell"})
        address = data[0].findAll("p")
        phone = data[1].find("a").text
        hours_of_operation = data[2].find("p").text
        latitude, longitude = re.findall(
            r"/@(-?[\d\.]+),(-?[\d\.]+)", address[1].find("a").get("href")
        )[0]
        address = address[0].get_text(separator="|", strip=True).split("|")
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        zip_postal = address[1]
        location_name = city + ", " + state
        yield SgRecord(
            locator_domain="https://www.worldwidestereo.com/",
            page_url=page_url,
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude=latitude.strip(),
            longitude=longitude.strip(),
            hours_of_operation=hours_of_operation.strip(),
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
