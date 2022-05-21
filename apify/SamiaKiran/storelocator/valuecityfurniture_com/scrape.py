from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "valuecityfurniture_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.valuecityfurniture.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.valuecityfurniture.com/api/environment/config"
        log.info("Fetching the token for the API.....")
        r = session.get(url, headers=headers)
        token = r.text.split('"SearchServicesApiKey":"')[1].split('"')[0]
        api_url = "https://api.blueport.com/v1/store?key=" + token
        loclist = session.get(api_url, headers=headers).json()["stores"]
        for loc in loclist:
            try:
                page_url = DOMAIN + loc["storeUrl"]
            except:
                continue
            location_name = loc["storeName"]
            store_number = loc["storeKey"]
            address = loc["storeAddress"]
            phone = address["telephone"]
            street_address = address["thoroughfare"]
            log.info(page_url)
            city = address["locality"]
            state = address["administrativeArea"]
            zip_postal = address["postalCode"]
            country_code = address["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hour_list = loc["storeHours"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["day"]
                time = hour["storeHours"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
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
