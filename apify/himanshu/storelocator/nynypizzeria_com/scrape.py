import re
import unicodedata
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

website = "nynypizzeria_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://nynypizzeria.com/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://nynypizzeria.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "div",
            {
                "class": "fusion-fullwidth fullwidth-box fusion-builder-row-2 fusion-flex-container nonhundred-percent-fullwidth non-hundred-percent-height-scrolling"
            },
        )
        loclist = loclist.findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            location_name = loc.text
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                phone = (
                    soup.find("div", {"class": "fusion-column-content"}).find("a").text
                )
                hours_of_operation = r.text.split("Hours of Operation")[1].split(
                    '*Due"/>'
                )[0]
                hours_of_operation = re.sub(pattern, "\n", hours_of_operation).replace(
                    "\n", " "
                )
                hours_of_operation = strip_accents(hours_of_operation)
                if '"/>' in hours_of_operation:
                    hours_of_operation = hours_of_operation.split('"/>')[0]
            except:
                phone = MISSING
                hours_of_operation = MISSING
            raw_address = (
                soup.find("iframe")["src"]
                .split("language=en&q=")[1]
                .split("&maptype")[0]
                .replace("+", " ")
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city.replace("Tamps", "Tampa")
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
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
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
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
