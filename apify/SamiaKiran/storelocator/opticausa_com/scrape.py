import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "opticausa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.opticausa.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.opticausa.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "col-md-4 col-12 p-4"})
        for link in linklist:
            page_url = link.find("a", string=re.compile("Store Details"))["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("div", {"class": "col-12 col-md-4 text-center"})
            address = (
                temp.find("address").get_text(separator="|", strip=True).split("|")
            )
            location_name = temp.find("h1").text
            phone = temp.select_one("a[href*=tel]").text
            if len(address) == 6:
                street_address = address[0]
                address = address[1].split(",")
            else:
                street_address = address[1]
                address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            hours_of_operation = (
                temp.find("section", {"id": "hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
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
                latitude=MISSING,
                longitude=MISSING,
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
