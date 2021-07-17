import json
from lxml import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
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
website = "unfi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    if True:
        identities = set()
        with SgChrome() as driver:
            driver.get("https://www.unfi.com/locations")
            data_runfi = html.fromstring(driver.page_source, "lxml")
            data_raw = data_runfi.xpath(
                '//script[@type="text/javascript" and contains(., "jQuery.extend(Drupal.settings")]/text()'
            )
            data_raw = "".join(data_raw)
            data_raw = data_raw.split("jQuery.extend(Drupal.settings,")[-1]
            data_raw = data_raw.split(");")[0]

        loclist = json.loads(data_raw)["gmap"]
        for loc in loclist:
            linklist = loclist[loc]["markers"]
            for link in linklist:
                text = link["text"]
                soup = BeautifulSoup(text, "html.parser")
                latitude = link["latitude"]
                longitude = link["longitude"]
                street_address = soup.find("span", {"itemprop": "streetAddress"}).text
                log.info(street_address)
                city = soup.find("span", {"itemprop": "addressLocality"}).text.replace(
                    ",", ""
                )
                state = soup.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = soup.find("span", {"class": "postal-code"}).text
                location_name = link["markername"]
                if location_name == "unfi":
                    location_name = "UNFI Distribution Center"
                elif location_name == "unfi_canada":
                    location_name = "UNFI Canada Distribution Center"
                elif location_name == "tonys":
                    location_name = "Tony's Fine Foods Distribution Center"
                elif location_name == "alberts":
                    location_name = "Albert's Fresh Produce Distribution Center"
                else:
                    location_name = "SUPERVALU/UNFI Distribution Center"
                if "2995 Oates Street" in street_address:
                    location_name = "Nor-Cal Produce Distribution Center"

                if (
                    "Tony's Fine Foods Distribution Center" in location_name
                    and "50 Charles Lindbergh Boulevard" in street_address
                ):
                    continue
                if (
                    "Tony's Fine Foods Distribution Center" in location_name
                    and "12745 Earhart Ave" in street_address
                ):
                    continue
                if (
                    "Tony's Fine Foods Distribution Center" in location_name
                    and "2722 Commerce Way" in street_address
                ):
                    continue

                try:
                    phone = soup.find("span", {"itemprop": "telephone"}).text
                except:
                    phone = "<MISSING>"
                identity = (
                    str(street_address)
                    + ","
                    + str(city)
                    + ","
                    + str(state)
                    + ","
                    + str(zip_postal)
                    + ","
                    + str(location_name)
                )
                if identity in identities:
                    continue
                log.info(location_name)
                identities.add(identity)
                yield SgRecord(
                    locator_domain="https://www.unfi.com/",
                    page_url="https://www.unfi.com/locations",
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone.strip(),
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
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
