from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gretchenscottdesigns_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.gretchenscottdesigns.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://viewer.blipstar.com/searchdbnew?uid=5434986&lat=27.8333&lng=-81.717&value=10000&r=100000000000"
        loclist = session.get(url, headers=headers).json()[1:]
        for loc in loclist:
            location_name = loc["n"]
            log.info(location_name)
            store_number = loc["bpid"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            address = loc["a"]
            raw_address = (
                BeautifulSoup(address, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
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
            try:
                country_code = loc["c"]
            except:
                country_code = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.gretchenscottdesigns.com/locator",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
