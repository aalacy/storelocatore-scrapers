from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


session = SgRequests()
website = "kloecknermetals_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.kloecknermetals.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        with SgChrome() as driver:
            driver.get("https://www.kloecknermetals.com/contact/kloeckner-branches/")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            loclist = soup.findAll("a", {"class": "c-red ng-binding"})
            for loc in loclist:
                page_url = loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers, allow_redirects=True)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find(
                    "div", {"class": "size-1_3em c-black f-regular"}
                ).text
                temp_address = soup.find("div", {"class": "size-1_1em"})
                try:
                    phone = temp_address.find("a").text
                except:
                    phone = MISSING
                try:
                    address = (
                        temp_address.find("div", {"class": "pb-0_5em"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                except:
                    temp_address = soup.findAll("div", {"class": "size-1_1em"})[4]
                    phone = temp_address.find("a").text
                    address = (
                        temp_address.find("div", {"class": "pb-0_5em"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                address = address.replace(",", " ")
                formatted_addr = parser.parse_address_intl(address)
                street_address = formatted_addr.street_address_1
                if street_address is None:
                    street_address = formatted_addr.street_address_2
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zip_postal = formatted_addr.postcode
                country_code = "US"
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
