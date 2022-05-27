from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "carshoe_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.carshoe.com/eu/en.html"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.carshoe.com/eu/en/store-locator.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "component-storeLocatorDetail"})
        for loc in loclist:
            location_name = loc.find("h1").text
            log.info(location_name)

            raw_address = (
                loc.find("address")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            phone = (
                loc.find("div", {"class": "telephone"})
                .findAll("p")[2]
                .text.replace("T.", "")
            )
            hours_of_operation = loc.find("div", {"class": "opening-hours"}).findAll(
                "p"
            )
            hours_of_operation = " ".join(x.text for x in hours_of_operation[:-1])
            hours_of_operation = hours_of_operation.replace("Opening times", "")
            if "Virtual shopping" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Virtual shopping")[0]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "Italy"
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
                phone=phone.strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
