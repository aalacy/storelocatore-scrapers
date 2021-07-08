from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "levinfurniture_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.levinfurniture.com/store/locator/show-all-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "store-list"}).findAll(
            "div", {"class": "store-locator-stores-result-list-item"}
        )
        for loc in loclist:
            location_name = loc.find("span", {"class": "au-sl-store-name"}).text

            page_url = (
                "https://www.levinfurniture.com/store"
                + loc.select_one("a[href*=store]")["href"]
            )
            log.info(page_url)
            street_address = loc.find("span", {"itemprop": "streetAddress"}).text
            state = loc.find("span", {"itemprop": "addressRegion"}).text
            city = loc.find("span", {"itemprop": "addressLocality"}).text
            zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
            phone = loc.find("span", {"itemprop": "telephone"}).text
            hours_of_operation = (
                loc.find("div", {"class": "store-hours-table"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            yield SgRecord(
                locator_domain="https://www.levinfurniture.com/",
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
