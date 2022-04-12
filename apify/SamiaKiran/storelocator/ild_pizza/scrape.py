import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


session = SgRequests()
website = "ild_pizza"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://ild.pizza/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://ild.pizza/departments"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split('<departments-list :departments="')[1]
            .split('"></departments-list>')[0]
            .replace("&quot;", '"')
        )
        loclist = json.loads(loclist)
        for loc in loclist:
            page_url = "https://ild.pizza/orders/create?department=" + str(
                loc["product_types"][0]["pivot"]["department_id"]
            )
            log.info(page_url)
            location_name = strip_accents(loc["name"])
            store_number = loc["id"]
            phone = MISSING
            street_address = strip_accents(loc["address"])
            city = strip_accents(loc["city"])
            state = MISSING
            zip_postal = loc["zipcode"]
            country_code = "Denmark"
            latitude = loc["coordinates"]["lat"]
            longitude = loc["coordinates"]["lon"]
            hours_of_operation = loc["opening_hours"]
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
