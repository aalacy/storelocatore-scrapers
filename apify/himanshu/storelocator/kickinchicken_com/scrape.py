from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "kickinchicken_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.kickinchicken.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.kickinchicken.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(class_="location-content")
        for loc in loclist:
            page_url = "https://www.kickinchicken.com" + loc.find_all("a")[-1]["href"]
            log.info(page_url)
            if "food-truck" in page_url:
                continue
            if "/locations/" in page_url:
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                address = (
                    soup.find("div", {"class": "address"})
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
                location_name = soup.find("h1").text
                hours_of_operation = (
                    soup.find("div", {"class": "widget hours loc-hour"})
                    .find("p")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("-ish", "")
                )
            else:
                page_url = url
                location_name = loc.find(class_="title").text
                address = (
                    loc.find("div", {"class": "address"})
                    .get_text(separator="|", strip=True)
                    .replace("Charleston ", "Charleston, ")
                    .split("|")
                )
                hours_of_operation = MISSING
            street_address = address[0].replace(",", "")
            phone = address[-1]
            if "," in phone:
                phone = MISSING
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
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
