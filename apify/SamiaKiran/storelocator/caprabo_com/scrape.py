import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "https://caprabo.com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://caprabo.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.caprabo.com/system/modules/com.caprabo.mrmmccann.caprabocom.formatters/resources/js/localizador.js"
        r = session.get(url, headers=headers)
        loclist = json.loads(r.text.split("var json =")[1].split("}];")[0] + "}]")
        for loc in loclist:
            location_name = MISSING
            longitude = loc["longitud"].replace(",", ".")
            latitude = loc["latitud"].replace(",", ".")
            phone = loc["telefono"]
            log.info(phone)
            street_address = strip_accents(loc["direccion"])
            city = strip_accents(loc["municipio"])
            state = strip_accents(loc["provincia"])
            zip_postal = loc["cp"]
            country_code = "SPAIN"
            hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.caprabo.com/ca/home/localizador-de-supermercados/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
