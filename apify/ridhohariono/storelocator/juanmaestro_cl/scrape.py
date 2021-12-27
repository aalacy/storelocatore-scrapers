from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "juanmaestro.cl"
LOCATION_URL = "https://www.juanmaestro.cl/Nuestroslocales"
API_URL = "https://api.getjusto.com/graphql?operationName=getStoresZones"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Content-Type": "application/json",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    payload = {
        "operationName": "getStoresZones",
        "variables": {"websiteId": "rPeT8PpL8w67BcpQc"},
        "query": "query getStoresZones($websiteId: ID) {\n  stores(websiteId: $websiteId) {\n    items {\n      _id\n      name\n      phone\n      humanSchedule {\n        days\n        schedule\n        __typename\n      }\n      acceptDelivery\n      acceptGo\n      zones {\n        _id\n        deliveryLimits\n        __typename\n      }\n      address {\n        placeId\n        location\n        address\n        addressSecondary\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }
    data = session.post(API_URL, headers=HEADERS, json=payload).json()
    for row in data["data"]["stores"]["items"]:
        location_name = row["name"]
        street_address = row["address"]["address"].strip()
        city = row["address"]["addressSecondary"].split(",")[0]
        state = MISSING
        zip_postal = MISSING
        phone = row["phone"]
        country_code = "CL"
        store_number = MISSING
        location_type = row["__typename"]
        hoo = ""
        for hday in row["humanSchedule"]:
            hoo += hday["days"] + ": " + hday["schedule"] + ","
        hours_of_operation = hoo.rstrip(",")
        latitude = row["address"]["location"]["lat"]
        longitude = row["address"]["location"]["lng"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
