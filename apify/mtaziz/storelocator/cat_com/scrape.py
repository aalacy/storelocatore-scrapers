from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("cat_com")
DOMAIN = "cat.com"
MISSING = SgRecord.MISSING
API_ENDPOINT_URL = "https://www.cat.com/content/catdotcom/en_US/support/dealer-locator/jcr:content/CATSectionArea/Copy%20of%20dealerlocator_1797052033.dealer-locator.html?searchType=location&maxResults=4500&searchDistance=20000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&searchValue=-150.4352207%2C60.9951298"


headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


def fetch_data():
    with SgRequests() as session:
        x = 0
        while True:
            x = x + 1
            try:
                data_json = session.get(
                    API_ENDPOINT_URL, headers=headers, timeout=500
                ).json()
                break
            except Exception as e:
                logger.info("")
                logger.info(e)
                if x == 10:
                    raise Exception(
                        "Make sure this ran with a Proxy, will fail without one"
                    )
                continue

        logger.info("JSON data being loaded...")

        for idx, _ in enumerate(data_json[0:]):
            page_url = ""
            purl = _["locationWebSite"]
            if purl:
                page_url = purl
            else:
                page_url = MISSING
            logger.info(f"[{idx}] Page URL: {page_url}")

            location_name = _["dealerName"]
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            street_address = _["siteAddress"]
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = _["siteCity"]
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = _["siteState"]
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = _["sitePostal"]
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Postal: {zip_postal}")

            country_code = _["countryCode"]
            country_code = country_code if country_code else MISSING
            logger.info(f"[{idx}] Country Code: {country_code}")

            store_number = _["dealerLocationId"]
            store_number = store_number if store_number else MISSING
            logger.info(f"[{idx}] Store Number: {store_number}")

            try:
                phone = _["stores"][0]["phoneNumbers"][0]["phoneNumber"]
            except:
                phone = MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            # Location Type
            location_type = ""
            location_type1 = []
            for s in _["stores"][0]["services"]:
                t = s["serviceDesc"]
                location_type1.append(t)
            if location_type1:
                location_type = "; ".join(location_type1)
            else:
                location_type = MISSING

            # Latlng
            latitude = _["latitude"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] Latitude: {latitude}")

            longitude = _["longitude"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] Longitude: {longitude}")

            # Hours of Operation
            fri = _["stores"][0]["storeHoursFri"]
            sat = _["stores"][0]["storeHoursSat"]
            sun = _["stores"][0]["storeHoursSun"]
            mon = _["stores"][0]["storeHoursMon"]
            tue = _["stores"][0]["storeHoursTue"]
            wed = _["stores"][0]["storeHoursWed"]
            thu = _["stores"][0]["storeHoursThu"]
            weekdays = ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
            weekdays_list = [fri, sat, sun, mon, tue, wed, thu]
            hoo = []

            for idx1, wd in enumerate(weekdays_list):
                if wd:
                    dt = weekdays[idx1] + " " + wd
                    hoo.append(dt)
                else:
                    dt = weekdays[idx1] + " "
                    hoo.append(dt)

            if hoo:
                hours_of_operation = "; ".join(hoo)
            else:
                hours_of_operation = MISSING
            logger.info(f"[{idx}] HOO: {hours_of_operation}")

            raw_address = ""
            raw_address = raw_address if raw_address else MISSING
            logger.info(f"[{idx}] Raw Address: {raw_address}")
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
