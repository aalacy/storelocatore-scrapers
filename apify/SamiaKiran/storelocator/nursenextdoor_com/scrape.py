from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "nursenextdoor_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://nursenextdoor.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.nursenextdoor.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        country_list = soup.find("div", {"class": "tabs__content-wrapper"}).findAll(
            "div", {"class": "tabs__content"}
        )
        for country in country_list:
            if country["id"] == "tab-1":
                country_code = "US"
            else:
                country_code = "CA"
            state_list = country.findAll("div", {"class": "locations-flex-list__group"})
            for temp in state_list:
                state = temp.find("h3").text
                location_name = state
                loclist = temp.findAll("li", {"class": "locations-flex-list__item"})
                for loc in loclist:
                    page_url = loc.find("a")
                    city = page_url.text
                    page_url = page_url["href"]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    phone = (
                        soup.find("div", {"class": "footer__flex"})
                        .select_one("a[href*=tel]")
                        .text.replace("CARE", "")
                    )
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=MISSING,
                        city=city,
                        state=state,
                        zip_postal=MISSING,
                        country_code=country_code,
                        store_number=MISSING,
                        phone=phone.strip(),
                        location_type=MISSING,
                        latitude=MISSING,
                        longitude=MISSING,
                        hours_of_operation=MISSING,
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
