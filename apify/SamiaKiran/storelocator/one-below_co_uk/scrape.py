from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "one-below_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.one-below.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.one-below.co.uk/a-z-stores"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("Store A-Z directory")[1]
            .split("Contact Us</span></span></span></p>")[0]
            .lower()
            .split("opening hours:")
        )
        for idx, loc in enumerate(loclist):
            loc = BeautifulSoup(loc, "html.parser")
            loc = loc.findAll("p")
            try:
                location_name = (
                    loc[-5].get_text(separator="|", strip=True).replace("|", " ")
                )
                if "onebelow" not in location_name:
                    location_name = loc[4].text
            except:
                continue
            log.info(location_name)
            raw_address = loc[-4].get_text(separator="|", strip=True).replace("|", " ")
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            phone = loc[-3].text.replace("telephone:", "")
            hours_of_operation = loclist[idx + 1]
            hours_of_operation = (
                BeautifulSoup(hours_of_operation, "html.parser")
                .get_text(separator="{", strip=True)
                .split("{")[0]
                .replace("|", "")
            )
            country_code = "UK"
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
                hours_of_operation=hours_of_operation.strip(),
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
