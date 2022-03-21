from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "saintspub.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    r = session.get("https://saintspub.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    field = soup.find_all("div", {"class": "et_pb_blurb_container"})
    for i in field:
        location_name = i.find("h4", {"class": "et_pb_module_header"}).find("span").text
        temp = i.find("div", {"class": "et_pb_blurb_description"})
        addr = temp.find("p").text.split(",")
        phone = temp.select_one("a[href*=tel]").text
        street_address = addr[0]
        city = addr[1]
        state = addr[2]
        yield SgRecord(
            locator_domain="https://saintspub.com/",
            page_url="https://saintspub.com/locations/",
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal="<MISSING>",
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<MISSING>",
            longitude="<MISSING>",
            hours_of_operation="<MISSING>",
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
