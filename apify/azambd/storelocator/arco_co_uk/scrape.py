import time
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "arco.co.uk"
website = "https://www.arco.co.uk"

MISSING = SgRecord.MISSING


session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_stores(url):
    return session.get(url).json()["data"]


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_objectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def get_hoo(hooinfo):
    hoo = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        hoo.append(f"{day}: {hooinfo[day]}")

    return "; ".join(hoo)


def fetch_data():
    stores = fetch_stores(
        website + "/store-finder?q=&page=0&productCode=&show=All&fetchAll=true"
    )
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        location_name = get_json_objectVariable(store, "displayName")
        store_number = get_json_objectVariable(store, "name")
        page_url = "https://www.arco.co.uk/store-finder"
        location_type = "Store"
        street_address = get_json_objectVariable(store, "line1")
        street_address = street_address.replace("&amp;", " &")
        city = get_json_objectVariable(store, "town")
        zip_postal = get_json_objectVariable(store, "postalCode")
        state = MISSING
        country_code = get_json_objectVariable(store, "country")
        phone = get_json_objectVariable(store, "phone")
        latitude = get_json_objectVariable(store, "latitude")
        longitude = get_json_objectVariable(store, "longitude")
        hoos = get_json_objectVariable(store, "features.0.openings")
        hours_of_operation = get_hoo(hoos)

        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
