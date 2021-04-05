from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import re
from bs4 import BeautifulSoup

website = "maxsmexicancuisine.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def parse_geo(url):
    lon = re.findall(r"\,(--?[\d\.]*)", url)[0]
    lat = re.findall(r"\@(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    if True:
        url = "https://www.maxsmexicancuisine.com/contact"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "_1Z_nJ"})
        for loc in loclist:
            if loc.find("h5") is None:
                continue
            location_name = loc.find("h5").text
            street_address = "<MISSING>"
            temp = loc.findAll("p")
            hours_of_operation = " ".join(hour.text for hour in temp[0:4])
            street_address = temp[4].text
            coords = temp[4].find("a")["href"]
            latitude, longitude = parse_geo(coords)
            phone = temp[6].text
            temp = temp[5].text.split()
            city = temp[0].replace(",", "")
            state = temp[1]
            zip_postal = temp[2]
            yield SgRecord(
                locator_domain="https://www.maxsmexicancuisine.com/",
                page_url="https://www.maxsmexicancuisine.com/contact",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours_of_operation,
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
