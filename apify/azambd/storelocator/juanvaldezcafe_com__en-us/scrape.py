import time
import json

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "juanvaldezcafe.com/en-us"

MISSING = SgRecord.MISSING
website = "https://www.juanvaldezcafe.com/"
jsonUrl = "https://api.storerocket.io/api/user/OdJEDYo4WE/locations"

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None:
        value = noVal
    return value


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def fetchData():
    body = session.get(jsonUrl)
    response = json.loads(body.text)
    restaurants = response["results"]["locations"]
    log.info(f"Total restaurants = {len(restaurants)}")

    for data in restaurants:
        locator_domain = DOMAIN
        store_number = str(getJSONObjectVariable(data, "id"))
        page_url_part1 = (
            "https://www.juanvaldezcafe.com/tienda-online/tiendas?location="
        )
        page_url_part2 = str(getJSONObjectVariable(data, "slug"))
        if page_url_part2 != "":
            page_url = page_url_part1 + page_url_part2
        else:
            page_url = website
        location_name = str(getJSONObjectVariable(data, "name"))
        location_type = str(getJSONObjectVariable(data, "location_type_name"))
        city = str(getJSONObjectVariable(data, "city"))
        zip_postal = str(getJSONObjectVariable(data, "postcode"))
        state = str(getJSONObjectVariable(data, "state"))
        country_code = str(getJSONObjectVariable(data, "country"))
        phone = getJSONObjectVariable(data, "phone")
        latitude = str(getJSONObjectVariable(data, "lat"))
        longitude = str(getJSONObjectVariable(data, "lng"))
        raw_address = str(getJSONObjectVariable(data, "address"))
        street_address = str(getJSONObjectVariable(data, "address_line_1"))

        address2 = getJSONObjectVariable(data, "address_line_2")
        if address2 != MISSING and street_address != address2:
            street_address = street_address + " " + address2

        operations = []
        for day in days:
            if day in data and data[day] is not None:
                operations.append(f"{day}: {data[day]}")
        hours_of_operation = ", ".join(operations)

        yield SgRecord(
            locator_domain=locator_domain,
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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
