from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

session = SgRequests()
website = "saje_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://saje.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.saje.com/store-locator/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("td", {"class": "store-location-name"})
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            raw_address = (
                soup.find("div", {"class": "store-address1"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Address", "")
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = pa.country
            country_code = country_code.strip() if country_code else MISSING
            location_name = soup.find("div", {"class": "store-details-name"}).text
            phone = (
                soup.find("div", {"class": "store-phone"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Phone ", "")
            )
            hours_of_operation = (
                soup.find("div", {"class": "store-hours-main"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store Hours", "")
            )
            if "Holiday" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Holiday")[0]
            latitude, longitude = (
                r.text.split("var myLatlng = new google.maps.LatLng(")[1]
                .split(");")[0]
                .split(",")
            )
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
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
