from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "8ozburgerandco_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.8ozburgerandco.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.8ozburgerandco.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "col sqs-col-3 span-3"}).find(
            "div", {"class": "sqs-block-content"}
        )
        loclist = str(loclist).split(
            '<p class="" style="white-space:pre-wrap;">Free 60 minute underground parking. </p>'
        )
        for loc in loclist:
            loc = loc + "</div>"
            soup = BeautifulSoup(loc, "html.parser")
            location_name = soup.find("h3").text
            log.info(location_name)
            address = soup.findAll("p")
            phone = address[-1].text.replace("Phone orders:", "")
            hours_of_operation = (
                address[1].get_text(separator="|", strip=True).replace("|", " ")
            )
            address = address[0].text.split(",")
            street_address = address[0]
            city = address[1]
            state = "WA"
            zip_postal = MISSING
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
