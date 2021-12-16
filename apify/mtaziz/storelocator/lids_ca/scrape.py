from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger(logger_name="lids_ca")

DOMAIN = "lids.ca"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        URL_API_ENDPOINT = "https://www.lids.ca/api/data/v2/stores/514601?lat=43.6564616&long=-79.3805647&num=1000&shipToStore=false"
        data_list = session.get(URL_API_ENDPOINT, headers=headers).json()
        for idx, item in enumerate(data_list[0:]):
            locator_domain = DOMAIN
            logger.info(f"[{idx}] [Locator Domain----] {locator_domain}")

            page_url = "https://lids.ca" + item["taggedUrl"]

            # The is one of the page URLs which does work or can not be accessed
            if "calidssunridgemall" in page_url:
                page_url = "<INACCESSIBLE>"
            logger.info(f"[{idx}] [Page URL----------] {page_url}")

            location_name = item["name"]
            logger.info(f"[{idx}] [Location Name-----] {location_name}")

            address_line1 = item["address"]["addressLine1"]
            street_address = address_line1 if address_line1 else MISSING
            logger.info(f"[{idx}] [Street Address----] {street_address}")

            city = item["address"]["city"]
            city = city if city else MISSING
            logger.info(f"[{idx}] [City--------------] {city}")

            state = item["address"]["state"]
            state = state if state else MISSING
            logger.info(f"[{idx}] [State-------------] {state}")

            zip_postal = item["address"]["zip"]
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] [Zip Code----------] {zip_postal}")

            country_code = item["address"]["country"]
            country_code = country_code if country_code else MISSING
            logger.info(f"[{idx}] [Country Code------] {country_code}")

            store_number = item["storeId"]
            logger.info(f"[{idx}] [Store Number------] {store_number}")

            # Phone
            phone = item["phone"]
            logger.info(f"[{idx}] [Phone-------------] {phone}")

            # Location Type
            location_type = ""
            location_type = location_type if location_type else MISSING

            # Latlng
            latitude = item["location"]["coordinate"]["latitude"]
            longitude = item["location"]["coordinate"]["longitude"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] [latitude----------] {latitude}")
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] [Longitude---------] {longitude}")

            # Hours of Hours
            mon = item["mondayOpen"] + " - " + item["mondayClose"]
            tue = item["tuesdayOpen"] + " - " + item["tuesdayClose"]
            wed = item["wednesdayOpen"] + " - " + item["wednesdayClose"]
            thu = item["thursdayOpen"] + " - " + item["thursdayClose"]
            fri = item["fridayOpen"] + " - " + item["fridayClose"]
            sat = item["saturdayOpen"] + " - " + item["saturdayClose"]
            sun = item["sundayOpen"] + " - " + item["sundayClose"]
            hours_of_operation = f"Mon: {mon}; Tue: {tue}; Wed: {wed}, Thu: {thu}, Fri: {fri}, Sat: {sat}, Sun: {sun}"
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING
            logger.info(f"[{idx}] [Hours of Operation] {hours_of_operation}")

            raw_address = MISSING
            logger.info(f"[{idx}] [Raw Address-------] {raw_address}")
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
