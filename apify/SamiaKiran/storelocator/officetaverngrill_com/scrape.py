from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "officetaverngrill_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://www.officetaverngrill.com/locations-new"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"id": "sortMain"}).findAll(
        "div", {"data-spansize": "6"}
    )
    for loc in loclist:
        temp = loc.findAll("div", {"class": "row js-group-row"})
        location_name = temp[1].find("p", {"class": "fp-el"}).text
        log.info(location_name)
        hours_of_operation = (
            temp[2].get_text(separator="|", strip=True).replace("|", " ")
        )
        phone = temp[4].text.split("call us at")[1].split("or Order")[0]
        address = temp[6].text.split(",")
        street_address = address[0]
        city = address[1]
        address = address[2].split()
        state = address[0]
        zip_postal = address[1]
        yield SgRecord(
            locator_domain="https://www.officetaverngrill.com/",
            page_url="https://www.officetaverngrill.com/locations-new",
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone.strip(),
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
