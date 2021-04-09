from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "risebiscuitsdonuts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://risebiscuitschicken.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "entry-content"}).findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "entry-title"}).text
            hours_of_operation = soup.find("div", {"class": "loc-hours"}).get_text(separator='|', strip=True).replace('|'," ")
            phone = soup.find("div", {"class": "loc-contact"}).findAll("a")[1].text
            address = (
                soup.find("div", {"class": "loc-address"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = " ".join(x for x in address[:-1])
            address = address[-1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            yield SgRecord(
                locator_domain="https://risebiscuitschicken.com/",
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
