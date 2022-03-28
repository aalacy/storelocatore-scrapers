import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rexel_pt"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://rexel.pt/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.rexel.pt/lojas/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("stores: ")[1].split(" ],")[0].split("}")[:-1]
        for loc in loclist:
            location_name = strip_accents(
                loc.split("name: ")[1].split(",")[0].replace("'", "")
            )
            log.info(location_name)
            address = loc.split("address: ")[1].split("',")[0].replace("'", "")
            address = BeautifulSoup(address, "html.parser")
            address = address.get_text(separator="|", strip=True).split("|")
            hours_of_operation = strip_accents(address[-1].replace("'", ""))

            raw_address = address[0] + " " + address[1]
            pa = parse_address_intl(strip_accents(raw_address))

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            city = loc.split("city: ")[1].split("',")[0].replace("'", "")
            zip_postal = (
                loc.split("zipcode: ")[1].split("',")[0].replace("'", "").split()[0]
            )
            latitude = loc.split("latitude: ")[1].split(",")[0]
            longitude = loc.split("longitude: ")[1].split(",")[0]
            country_code = "PT"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
