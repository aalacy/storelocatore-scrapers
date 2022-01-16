from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bishops_co"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bishops.co/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        for page in range(1, 7):
            url = f"https://bishops.co/search-results/{page}/?form=3"
            r = session.get(url, headers=headers)
            if "There are no locations found" in r.text:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll(
                "div", {"class": "location-post-block-content matchheight"}
            )
            for loc in loclist:
                page_url = loc.find("a")["href"]
                log.info(page_url)
                location_name = loc.find("h3").text
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                temp = soup.findAll("div", {"class": "col span_3_of_12"})
                if len(temp) > 3:
                    temp = temp[1:-1]
                address = temp[0].find("a")
                try:
                    phone = temp[2].find("a").text
                except:
                    phone = MISSING
                hours_of_operation = (
                    temp[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Hours", "")
                )
                try:
                    coords = address["href"].split("@")[1].split(",")
                    latitude = coords[0]
                    longitude = coords[1]
                except:
                    latitude = MISSING
                    longitude = MISSING
                raw_address = address.text
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = "US"
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
