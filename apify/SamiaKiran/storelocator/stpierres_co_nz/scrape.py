import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "stpierres_co_nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://stpierres.co.nz/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://stpierres.co.nz/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("article", {"class": "store"})
        for loc in loclist:
            location_name = strip_accents(
                loc.find("h5", {"class": "store-name"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            log.info(location_name)
            phone = soup.select_one("a[href*=tel]").text
            raw_address = strip_accents(
                loc.find("p", {"class": "store-address"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            # Parse the address
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            try:
                hours_of_operation = (
                    loc.find("div", {"class": "store-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .split("Normal Hours")[1]
                )
            except:
                hours_of_operation = (
                    loc.find("div", {"class": "store-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            if "(Hours" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("(Hours")[0]
            latitude = loc["data-lat"]
            longitude = loc["data-lng"]
            store_number = loc["data-store-id"]
            country_code = "NZ"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
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
