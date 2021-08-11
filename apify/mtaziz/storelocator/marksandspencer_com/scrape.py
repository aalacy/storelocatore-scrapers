from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MISSING = SgRecord.MISSING
DOMAIN = "marksandspencer.com"
API_ENDPOINT_URL = "https://api.marksandspencer.com/v1/stores?apikey=aVCi8dmPbHgHrdCv9gNt6rusFK98VokK&jsonp=angular.callbacks._2&latlong=51.500152587890625,-0.12623600661754608&limit=2000&radius=50000"
logger = SgLogSetup().get_logger("marksandspencer_com")
headers_api = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        r = session.get(API_ENDPOINT_URL, headers=headers_api, timeout=500)
        data = r.text.split("angular.callbacks._2(")[-1]
        r_text = r.text
        data = r_text.split("angular.callbacks._2(")[-1]
        data = data.rstrip(");")
        data = json.loads(data)
        data = data["results"]
    for d in data:
        locator_domain = "marksandspencer.com"
        page_url = MISSING
        location_name = d["name"]

        location_name = location_name if location_name else MISSING

        street_address = d["address"]["addressLine2"]
        street_address = street_address if street_address else MISSING

        city = d["address"]["city"]
        city = city if city else MISSING

        state = d["address"]["isoTwoCountryCode"]
        state = state if state else MISSING

        zip_postal = d["address"]["postalCode"]
        zip_postal = zip_postal if zip_postal else MISSING

        country_code = d["address"]["country"]
        country_code = country_code if country_code else MISSING

        store_number = d["id"]
        store_number = store_number if store_number else MISSING

        if "phone" in d:
            phone = d["phone"].strip()
        else:
            phone = MISSING

        location_type = d["storeType"]
        location_type = location_type if location_type else MISSING

        latitude = d["coordinates"]["latitude"]
        latitude = latitude if latitude else MISSING

        longitude = d["coordinates"]["longitude"]
        longitude = longitude if longitude else MISSING

        hours_of_operation = ""
        h1 = d["coreOpeningHours"]
        hours_of_operation = (
            str(h1)
            .replace("'", "")
            .replace("{", "")
            .replace("}", "")
            .replace("[", "")
            .replace("]", "")
            .replace("day: ", "")
            .replace(", close:", " -")
            .replace(" open:", "-")
            .replace("y,", "y ")
        )
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        raw_address = SgRecord.MISSING
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
