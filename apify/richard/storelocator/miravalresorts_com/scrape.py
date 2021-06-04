from bs4 import BeautifulSoup
from sglogging import sglog
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "miravalresorts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    with SgChrome() as driver:
        driver.get("https://www.miravalresorts.com/")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll("ul", {"class": "xsmall-up-1 medium-up-2 large-up-3"})[
            1
        ].findAll("li")
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            driver.get(page_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            temp_list = (
                soup.findAll("div", {"class": "footer--column"})[3]
                .get_text(separator="|", strip=True)
                .split("|")[1:-1]
            )
            phone = temp_list[0].replace("Call", "")
            location_name = temp_list[1]
            street_address = temp_list[2]
            address = temp_list[3].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            yield SgRecord(
                locator_domain="https://www.miravalresorts.com/",
                page_url=page_url,
                location_name=location_name,
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
