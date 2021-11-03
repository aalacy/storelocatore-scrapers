from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

session = SgRequests()
website = "sharkclub_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://sharkclub.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.sharkclub.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "columns-5 content-column"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            r = session.get(page_url, headers=headers)
            log.info(page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "location-card-section"})
            raw_address = temp[0].findAll("p")[1].text
            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Hours Of Operation", "")
                .replace("::", "")
            )
            if "Closed until further notice" in hours_of_operation:
                hours_of_operation = MISSING
            phone = temp[2].find("a").text
            location_name = (
                soup.find("div", {"class": "location-title-container"}).find("h2").text
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
            if zip_postal.isnumeric():
                country_code = "US"
            else:
                country_code = "CA"
            coords = soup.find("div", {"class": "marker"})
            latitude = coords["data-lat"]
            longitude = coords["data-lng"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
