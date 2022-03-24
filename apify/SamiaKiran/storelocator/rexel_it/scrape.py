import json
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
website = "rexel_it"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://rexel.it"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://rexel.it/punti-vendita"
        r = session.get(url, headers=headers)
        loclist = r.text.split("originalPoints = ")[1].split("}]</script>")[0]
        loclist = json.loads(loclist + "}]")
        for loc in loclist:
            page_url = DOMAIN + loc["url"]
            location_name = strip_accents(loc["name"])
            log.info(page_url)
            store_number = loc["id"]
            description = loc["description"]
            soup = BeautifulSoup(description, "html.parser")
            description = soup.get_text(separator="|", strip=True).split("|")
            raw_address = strip_accents(description[0] + " " + description[1]).replace(
                "24066P", "24066 P"
            )
            phone = description[2].replace("Tel", "")
            hours_of_operation = strip_accents(
                soup.get_text(separator="|", strip=True).replace("|", " ")
            ).split("Lunedi  Venerdi")[1]
            hours_of_operation = "Lunedì – Venerdì" + hours_of_operation
            pa = parse_address_intl(strip_accents(raw_address))

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            if city == MISSING:
                city = raw_address.split()[-2]
            latitude = loc["lt"]
            longitude = loc["ln"]
            country_code = "IT"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
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
