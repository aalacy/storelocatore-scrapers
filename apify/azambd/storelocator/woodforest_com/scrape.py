import time
from concurrent.futures import ThreadPoolExecutor

from sgzip.static import static_zipcode_list, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

MISSING = "<MISSING>"
website = "https://woodforest.com"
searchUrl = f"{website}/Lib/WFNB.Functions.GetLocations.ashx?address=&city=&state=&distance=999&display=45&zipCode="
max_workers = 1
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def getHOO(hours):
    hours_of_operation = []
    for hour in hours:
        day = hour.get("day")
        status = hour.get("status")
        if status == "Closed":
            hours_of_operation.append(f"{day}: Closed")
        else:
            formated = hour.get("formattedHours")
            hours_of_operation.append(f"{day}: {formated}")

    hours_of_operation = ";".join(hours_of_operation)

    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"
    return hours_of_operation


def fetchSingleZip(zip_code):
    page_url = f"{searchUrl}{zip_code}"
    try:
        r = session.post(page_url)
    except Exception as e:
        return zip_code, [], e
    locations = getJSONObjectVariable(r.json(), "locations", [])
    result = []
    if locations is None:
        locations = []

    for location in locations:
        address = getJSONObjectVariable(location, "address", {})
        coordinates = getJSONObjectVariable(address, "coordinates", {})

        result.append(
            {
                "locator_domain": website,
                "page_url": page_url,
                "street_address": getJSONObjectVariable(address, "street"),
                "city": getJSONObjectVariable(address, "city"),
                "state": getJSONObjectVariable(address, "state"),
                "zip_postal": getJSONObjectVariable(address, "zipCode"),
                "country_code": "US",
                "latitude": getJSONObjectVariable(coordinates, "latitude"),
                "longitude": getJSONObjectVariable(coordinates, "longitude"),
                "location_name": getJSONObjectVariable(location, "institution.name"),
                "store_number": getJSONObjectVariable(location, "number"),
                "phone": getJSONObjectVariable(location, "phone"),
                "location_type": getJSONObjectVariable(location, "type.displayAs"),
                "hours_of_operation": getHOO(getJSONObjectVariable(location, "lobby")),
            }
        )

    return zip_code, result, None


def fetchData():
    zips = static_zipcode_list(radius=20, country_code=SearchableCountries.USA)
    log.info(f"Total zip codes = {len(zips)}")
    countZip = 0
    count = 0

    storeNumbers = []
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for zip_code, result, error in executor.map(fetchSingleZip, zips):
            if countZip % 100 == 0:
                log.info(f"total zip code = {countZip} total stores = {count}")

            countZip = countZip + 1
            if error is not None:
                continue

            for details in result:
                raw_address = f"{details['street_address']}, {details['city']}, {details['state']} {details['zip_postal']}"

                if details["store_number"] in storeNumbers:
                    continue
                storeNumbers.append(details["store_number"])
                count = count + 1
                yield SgRecord(
                    locator_domain=details["locator_domain"],
                    store_number=details["store_number"],
                    page_url=details["page_url"],
                    location_name=details["location_name"],
                    location_type=details["location_type"],
                    street_address=details["street_address"],
                    city=details["city"],
                    zip_postal=details["zip_postal"],
                    state=details["state"],
                    country_code=details["country_code"],
                    phone=details["phone"],
                    latitude=details["latitude"],
                    longitude=details["longitude"],
                    hours_of_operation=details["hours_of_operation"],
                    raw_address=raw_address,
                )


def scrape():
    start = time.time()
    log.info("Started")
    count = 0
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total row added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
