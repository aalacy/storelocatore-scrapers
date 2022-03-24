import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "amf-bowling_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://amf-bowling.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://amf-bowling.co.uk/centres"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<div class="centre-list__item centre-list__item')[1:]
        for loc in loclist:
            loc = '<div class="centre-list__item centre-list__item' + loc
            loc = BeautifulSoup(loc, "html.parser")
            page_url = loc.find("a", string=re.compile("Visit centre page"))["href"]
            log.info(page_url)
            location_name = loc.find("h3").text
            raw_address = (
                loc.find("div", {"class": "centre-list__details"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Hollywood Bowl", " ")
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = MISSING
            zip_postal = raw_address.split(",")[-1]

            phone = loc.select_one("a[href*=tel]").text
            hours_of_operation = (
                loc.find("table", {"class": "opening-times"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            coords = loc.find("div")
            latitude = coords["data-lat"]
            longitude = coords["data-lng"]
            country_code = "UK"
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
                latitude=latitude,
                longitude=longitude,
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
