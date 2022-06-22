import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "kamps.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://kamps.de"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://kamps.de/standorte"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var item = JSON.parse('")[1:]
        for loc in loclist:
            loc = loc.replace("&quot;", '"').split("}")[0] + "}}}"
            loc = json.loads(loc)
            loc = loc["properties"]
            page_url = DOMAIN + loc["website"]
            store_number = loc["geschaeftscode"]
            location_name = strip_accents(loc["unternehmen"])
            phone = loc["telefonnummer"]
            street_address = strip_accents(loc["adresszeile1"])
            log.info(page_url)
            city = strip_accents(loc["ort"])
            state = MISSING
            zip_postal = loc["postleitzahl"]
            country_code = loc["region"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = (
                "mo "
                + loc["oeffnungszeiten_mo"]
                + " di "
                + loc["oeffnungszeiten_di"]
                + " mi "
                + loc["oeffnungszeiten_mi"]
                + " do "
                + loc["oeffnungszeiten_do"]
                + " fr "
                + loc["oeffnungszeiten_fr"]
                + " sa "
                + loc["oeffnungszeiten_sa"]
            )
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
