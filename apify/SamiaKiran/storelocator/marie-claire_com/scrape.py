import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "marie-claire_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://marie-claire.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://stockist.co/api/v1/u8717/locations/all.js?callback=_stockistAllStoresCallback"
        r = session.get(url, headers=headers)
        loclist = r.text.split("stockistAllStoresCallback(")[1].split("}]);")[0]
        loclist = loclist + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            store_number = loc["id"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            try:
                street_address = loc["address_line_1"] + " " + loc["address_line_2"]
            except:
                street_address = loc["address_line_1"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = loc["country"]
            phone = loc["phone"]
            street_address = strip_accents(street_address)
            city = strip_accents(city)
            state = strip_accents(state)
            zip_postal = strip_accents(zip_postal)
            hour_list = loc["custom_fields"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["name"].rsplit("/")[-1]
                    + " "
                    + hour["value"]
                )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.marie-claire.com/pages/boutiques",
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
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
