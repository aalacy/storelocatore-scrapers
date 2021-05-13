import time

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()

MISSING = "<MISSING>"

DOMAIN = "juanvaldezcafe.com/en-us"

website = "https://www.juanvaldezcafe.com"

APIUrl = "https://storerocket.global.ssl.fastly.net/api/user/OdJEDYo4WE/locations"

log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


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
    jResp = requests_with_retry(APIUrl)
    jnodes = jResp["results"]["locations"]
    log.info(f"Total Locations = {len(jnodes)}")

    for data in jnodes:
        locator_domain = DOMAIN
        store_number = str(getJSONObjectVariable(data, "id"))
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
        address_line_1 = getJSONObjectVariable(data, "address_line_1")
        address_line_2 = getJSONObjectVariable(data, "address_line_2")
        street_address = address_line_1 + address_line_2

        hours_of_operation = ""
        operations = []
        for day in days:
            value = data[f"{day}"]
            if value is not None:
                operations.append(f"{day}: {value}")
                hours_of_operation = ", ".join(operations)
            else:
                hours_of_operation = MISSING

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
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
