from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "guzmanygomez_com_au"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.guzmanygomez.com.au"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.guzmanygomez.com.au/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location"})
        for loc in loclist:
            location_type = MISSING
            page_url = loc["data-url"]
            closed = loc.text.split(" - ")
            closed = closed[-1]
            if (
                closed == "TEMP CLOSED"
                or closed == "TEMPORARILY CLOSED"
                or closed == "CLOSED"
            ):
                location_type = "TEMPORARILY CLOSED"
            location_name = loc.find("h4").text
            log.info(page_url)
            raw_address = loc["data-address"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            store_number = loc["data-locationid"]
            latitude = loc["data-latitude"]
            longitude = loc["data-longitude"]
            hours_of_operation = (
                loc.findAll("table")[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if hours_of_operation == "Temporarily Closed":
                hours_of_operation = MISSING
                location_type = "TEMPORARILY CLOSED"
            elif "TEMP: CLOSED Mon" in hours_of_operation:
                hours_of_operation = hours_of_operation.replace("TEMP: CLOSED", "")
                location_type = "TEMPORARILY CLOSED"
            elif hours_of_operation == "TEMP: CLOSED":
                hours_of_operation = MISSING
                location_type = "TEMPORARILY CLOSED"
            phone = MISSING
            country_code = "AUS"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city,
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
