import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "walmart_com_ar"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://walmart.com.ar/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.walmart.com.ar/files/walmart.js"
        r = session.get(url, headers=headers)
        loclist = r.text.split('"stores": [{')[1].split("};")[0]
        loclist = json.loads("[{" + loclist)
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            log.info(location_name)
            phone = loc["phone"].split("/")[0]
            store_number = loc["id"]
            street_address = strip_accents(loc["address"])
            log.info(street_address)
            city = strip_accents(loc["city"])
            state = strip_accents(loc["state"])
            try:
                zip_postal = loc["ZIP"]
            except:
                zip_postal = MISSING
            country_code = "Argentina"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = loc["timetable"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.walmart.com.ar/institucional/encontra-tu-tienda",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
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
