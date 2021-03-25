from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "wagner-oil_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.wagner-oil.com/wagner-sites"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("section", {"id": "comp-kk48oayk"}).findAll(
            "div", {"data-testid": "mesh-container-content"}
        )
        for loc in loclist[2:]:
            if not loc.text:
                continue
            location_name = loc.find("h2").find("span").text
            log.info(location_name)
            temp_list = loc.findAll("div", {"class": "_1Z_nJ"})
            temp_list = temp_list[1].findAll("p")
            street_address = temp_list[1].find("span").text
            phone = temp_list[1].find("span").text
            address = location_name.split(",")
            city = address[0]
            state = address[1]
            page_url = "https://www.wagner-oil.com/wagner-sites"
            yield SgRecord(
                locator_domain="https://www.wagner-oil.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address,
                city=city.strip(),
                state=state.strip(),
                zip_postal="<MISSING>",
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
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
