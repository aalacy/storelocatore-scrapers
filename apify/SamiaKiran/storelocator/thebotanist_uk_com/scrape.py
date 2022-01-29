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
website = "thebotanist_uk_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://thebotanist.uk.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://thebotanist.uk.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("option")[1:]
        for loc in loclist:
            location_name = loc.text
            page_url = DOMAIN + loc["value"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            coords = soup.find("a", string=re.compile("Google Maps"))["href"]
            if "@" in coords:
                coords = coords.split("@")[1].split(",")
                latitude = coords[0]
                longitude = coords[1]
            else:
                latitude = MISSING
                longitude = MISSING
            address = soup.find("div", {"id": "find-us"}).findAll("div")
            phone = address[1].select_one("a[href*=tel]").text
            raw_address = (
                address[0].get_text(separator="|", strip=True).replace("|", " ")
            )
            hours_of_operation = (
                soup.find("div", {"id": "opening-times"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Opening times ", "")
            )
            if "*Bru" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("*Bru")[0]
            if "Christmas" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Christmas")[0]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if street_address == MISSING:
                street_address = raw_address.replace(city, "").replace(zip_postal, "")

            country_code = "UK"
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
                phone=phone.strip(),
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
