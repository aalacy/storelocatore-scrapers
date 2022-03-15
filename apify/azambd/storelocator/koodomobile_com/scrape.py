from lxml import html
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_2

website = "https://www.koodomobile.com"
MISSING = "<MISSING>"

data_url = "{}/koodo-store-locator/ajax/full?location={},{}"

session = SgRequests(proxy_rotation_failure_threshold=3)
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url)


def getHoo(response):
    body = html.fromstring(response, "lxml")
    data = body.xpath('//div[contains(@class, "store-hours")]')[0]
    texts = []
    for line in data.itertext():
        line = line.strip()
        if len(line) == 0 or "Call store " in line:
            continue
        if "0" in line or "5" in line or "Closed" in line:
            line = line + ";"
        texts.append(line)
    if len(texts) == 0:
        return MISSING
    return " ".join(texts).strip()[:-1]


def fetchData():

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=None,
        max_search_results=None,
        granularity=Grain_2(),
    )

    total_zip = 0
    uniqueIds = []
    for lat, lng in all_coords:
        total_zip = total_zip + 1
        url = data_url.format(website, lat, lng)
        response = request_with_retries(url)
        try:
            codeStores = json.loads(response.text)["stores"]
        except Exception as e:
            log.error(f"error loading {lat}, {lng}; messege:{e}")
            continue

        for key in codeStores.keys():
            store = codeStores[key]
            uniqueId = store["latlon"]
            if uniqueId in uniqueIds:
                continue
            uniqueIds.append(uniqueId)

            store_number = store["store_id"]
            page_url = "https://www.koodomobile.com/find-nearest-store?INTCMP=KMNew_FooterLINK_Stores_Stores"
            location_name = store["name"]
            location_type = MISSING
            street_address = store["address"]
            city = store["city"]
            zip_postal = store["postal_code"]
            state = store["province"]
            country_code = "CA"
            phone = store["phone_number"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            all_coords.found_location_at(latitude, longitude)
            hours_of_operation = getHoo(store["hours_window_content"])
            raw_address = f"{street_address}, {city}, {state} {zip_postal}"

            yield SgRecord(
                locator_domain=website,
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
        log.debug(
            f"{total_zip}. From {url} stores = {len(codeStores)}; total = {len(uniqueIds)}"
        )

    log.info(f"Final total zip={total_zip} stores={len(uniqueIds)}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
