import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rubinoshoes_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://rubinoshoes.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://stockist.co/api/v1/u8819/locations/all.js?callback=_stockistAllStoresCallback"
        r = session.get(url, headers=headers)
        loclist = json.loads(
            r.text.split("_stockistAllStoresCallback(")[1].split(");")[0]
        )
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            try:
                street_address = loc["address_line_1"] + " " + loc["address_line_2"]
            except:
                street_address = loc["address_line_1"]
            street_address = strip_accents(street_address)
            city = strip_accents(loc["city"])
            state = strip_accents(loc["state"])
            zip_postal = strip_accents(loc["postal_code"])
            country_code = "CA"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://rubinoshoes.com/pages/store-locator",
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
                hours_of_operation=MISSING,
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
