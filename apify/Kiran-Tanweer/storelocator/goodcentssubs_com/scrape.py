from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
DOMAIN = "goodcentssubs_com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = SgRecord.MISSING
API_URL = "https://locations.goodcentssubs.com/modules/multilocation/?near_location=65804&threshold=4000&distance_unit=miles&limit=1000"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
}


def fetch_data():
    if True:
        stores_req = session.get(API_URL, headers=headers).json()
        for stores in stores_req["objects"]:
            state = stores["state"]
            phone = stores["phonemap"]["phone"]
            pcode = stores["postal_code"]
            storeid = stores["id"]
            link = stores["location_url"]
            city = stores["city"]
            title = stores["location_name"]
            log.info(title)
            lng = stores["lon"]
            lat = stores["lat"]
            street = stores["street"]
            country = stores["country"]
            raw_address = stores["geocoded"]
            hours = stores["formatted_hours"]["primary"]["grouped_days"]
            hoos = []
            for hr in hours:
                hoo = f"{hr['label']}:{hr['content']}"
                hoos.append(hoo)

            hours_of_operation = ("; ").join(hoos)

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=country.strip(),
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
