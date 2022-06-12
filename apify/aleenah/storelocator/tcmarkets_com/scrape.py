from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tcmarkets_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://tcmarkets.com"
MISSING = SgRecord.MISSING


def fetch_data():
    res = session.get("https://tcmarkets.com/store-finder/")
    soup = BeautifulSoup(res.text, "html.parser")
    stores = soup.find_all("a", {"itemprop": "url"})
    del stores[0]
    for store in stores:
        page_url = store.get("href")
        log.info(page_url)
        if "https://tcmarkets.com/store-finder/dixon-ace-hardware/" in page_url:
            continue
        res = session.get(page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        temp = str(soup.find("div", {"class": "fl-rich-text"}))
        hours_of_operation = temp.split("Store Hours:")[1]
        hours_of_operation = (
            BeautifulSoup(hours_of_operation, "html.parser")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        if "Services Offered" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Services Offered")[0]
        if "Fuel Station" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Fuel Station")[0]
        if "Pharmacy Hours" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Pharmacy Hours")[0]
        address = temp.split("Store Address")[1]
        address = (
            BeautifulSoup(address, "html.parser")
            .get_text(separator="|", strip=True)
            .split("|")[:3]
        )
        phone = address[-1]
        raw_address = address[0] + " " + address[1]
        if "(" not in phone:
            phone = MISSING
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING

        location_name = city
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
