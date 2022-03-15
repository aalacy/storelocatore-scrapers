from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "eaglebankcorp_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.eaglebankcorp.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.eaglebankcorp.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "col-mb-6 col-3 locations"})
        for loc in loclist:
            street_address = loc.find("div", {"class": "street-address"}).text
            address = loc.find("div", {"class": "city-state-zip"}).text.split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            location_name = loc.find("div", {"class": "location-name"}).text
            log.info(location_name)
            phone = loc.find("div", {"class": "telephone"}).text
            country_code = "US"
            hours_of_operation = (
                loc.find("div", {"class": "business-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            try:
                location_type = loc.find("div", {"class": "services"}).text.replace(
                    "24/7 ATM Only;", ""
                )
                if "Non-Branch" not in location_type:
                    location_type = "Branch"
            except:
                location_type = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=location_type,
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
