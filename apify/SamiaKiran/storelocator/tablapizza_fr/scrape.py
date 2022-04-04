import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tablapizza_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://tablapizza.fr/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://pizzeria.tablapizza.fr/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var all_restaurants =")[1].split("}];")[0]
        loclist = json.loads(loclist + "}]")
        for loc in loclist:
            location_name = loc["post_title"]
            store_number = loc["ID"]
            page_url = loc["permalink"]
            log.info(page_url)
            address = loc["meta"]
            phone = address["telephone"]
            raw_address = strip_accents(
                address["adresse"] + " " + address["cp_ville"]
            ).replace("\n", " ")
            # Parse the address
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "FR"
            latitude = address["latitude"]
            longitude = address["longitude"]
            mon = "lundi " + address["horaires_lundi"]
            tue = " mardi " + address["horaires_mardi"]
            wed = " mercredi " + address["horaires_mercredi"]
            thu = " jeudi " + address["horaires_jeudi"]
            fri = " vendredi " + address["horaires_vendredi"]
            sat = " samedi " + address["horaires_samedi"]
            sun = " dimanche " + address["horaires_dimanche"]
            hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
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
