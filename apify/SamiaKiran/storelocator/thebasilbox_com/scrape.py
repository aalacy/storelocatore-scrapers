from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "thebasilbox_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.thebasilbox.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "locationsContainer clearfix"})
        for loc in loclist:
            page_url = "https://www.thebasilbox.com/locations/"
            temp = loc.find("div", {"class": "one-half first"})
            location_name = temp.find("h2").text
            log.info(location_name)
            address = temp.findAll("p")[1].text.split(",")
            street_address = " ".join(x for x in address[:-2])
            city = address[-2]
            address = address[-1].strip().split(" ", 1)
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = (
                loc.find("div", {"class": "one-fourth locationHours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Hours", "")
            )
            phone = (
                soup.find("div", {"class": "one-fourth locationContact"})
                .text.replace("Call Us", "")
                .replace("T", "")
            )
            yield SgRecord(
                locator_domain="https://www.thebasilbox.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="CAN",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
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
