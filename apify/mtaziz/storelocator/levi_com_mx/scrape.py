from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
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


DOMAIN = "levi.com.mx"
logger = SgLogSetup().get_logger("levi_com_mx")
MISSING = SgRecord.MISSING
MX_FIELDS = "address,client,cp,lat,lng,state,store,delegacion,local,tipo,phone,whatsapp"
API_ENDPOINT_URL = f"https://www.levi.com.mx/api/dataentities/SF/search?_fields={MX_FIELDS}&_schema=store-finder&_sort=state%20ASC"

headers_custom = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "rest-range": "resources=0-2000",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def fetch_data():
    with SgRequests() as http:
        data_list = http.get(API_ENDPOINT_URL, headers=headers_custom).json()
        logger.info(f"Pulling the data from {API_ENDPOINT_URL}")
        for _ in data_list:
            location_type_raw = _["tipo"]
            location_name = _["store"]
            location_type = ""
            if "store" in location_type_raw.lower():
                location_name = "Levi's Store"
                location_type = "STORE"
            elif "outlet" in location_type_raw.lower():
                location_name = "Levi's Outlet"
                location_type = "OUTLET"
            elif "retail" in location_type_raw.lower():
                location_name = "Levi's Retail Partner"
                location_type = "RETAILER"
            else:
                location_name = MISSING
                location_type = MISSING
            lt = location_type

            if "OUTLET" in lt or "RETAILER" in lt or "STORE" in lt:
                location_type = lt
            else:
                continue

            row = SgRecord(
                locator_domain=DOMAIN,
                page_url=MISSING,
                location_name=location_name,
                street_address=_["address"],
                city=_["delegacion"] or MISSING,
                state=_["state"] or MISSING,
                zip_postal=_["cp"] or MISSING,
                country_code="MX",
                store_number=MISSING,
                phone=_["phone"] or MISSING,
                location_type=location_type,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation=MISSING,
                raw_address=MISSING,
            )
            yield row


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
