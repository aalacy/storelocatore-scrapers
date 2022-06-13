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
website = "burton_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.burton.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.burton.com/ca/en/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        locations = soup.findAll("figure", {"class": "store-wrap"})
        for loc in locations:
            location_name = loc.find("h3", {"class": "text-h3-display"}).text.split(
                "—"
            )[0]
            if "-" in location_name:
                location_name = location_name.split("-")[0]
            raw_address = (
                loc.find("p", {"class": "address"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            pa = parse_address_intl(strip_accents(raw_address))

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = pa.country
            country_code = country_code.strip() if country_code else MISSING

            if state is not MISSING:
                if len(state) == 2 and zip_postal.isdigit():
                    country_code = "US"
                elif len(state) == 2:
                    country_code = "CA"
            phone = loc.find("span", {"itemprop": "telephone"}).text
            if "Coming" in phone:
                continue
            if zip_postal == MISSING and country_code == "CA":
                zip_postal = (
                    raw_address.replace(street_address, "")
                    .replace(city, "")
                    .replace(state, "")
                    .replace(street_address, "")
                    .replace(",", "")
                )
            page_url = (
                DOMAIN + loc.find("span", {"class": "view-details"}).find("a")["href"]
            )
            log.info(page_url)
            hours_of_operation = loc.findAll("meta", {"itemprop": "openingHours"})
            if hours_of_operation is None:
                hours_of_operation = MISSING
            else:
                hours_of_operation = " ".join(x["content"] for x in hours_of_operation)
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
