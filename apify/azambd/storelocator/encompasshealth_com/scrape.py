from lxml import html
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "encompasshealth.com"
website = "https://encompasshealth.com"
json_url = f"{website}/api/locationservice/locationsearchresults/no_facet/21.190439,72.87756929999999/1000/1/75000"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None or len(value) == 0:
        return noVal
    return value


def get_JSON_object_variable_type(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None:
        return noVal
    return value


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    response = request_with_retries(json_url)
    return json.loads(response.text)["data"]["locationDetailsSearchResponse"]


def get_url(store):
    urls = get_JSON_object_variable(store, "urls")
    for url in urls:
        if url["label"] == "More Details":
            return website + url["link"]


def get_hoo(page_url):
    response = request_with_retries(page_url)
    body = html.fromstring(response.text, "lxml")
    texts = body.xpath('//div[contains(@class, "locations-footer__hours")]/p/text()')
    hoo = []
    for text in texts:
        text = text.replace("Visiting hours", "").strip()
        if len(text) > 0:
            hoo.append(text)
    hoo = " ".join(hoo)
    hoo = (
        hoo.replace(
            "Please contact us for the most current visitor and support person policy.",
            "",
        )
        .replace("Please contact us for the most current visitor policy.", "")
        .replace(
            "Please contact us for most current visitation and support person policy.",
            "",
        )
        .replace("Visiting Hours", "")
        .strip()
    )
    if len(hoo) == 0:
        return MISSING
    return hoo


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    count = 0
    for store in stores:
        count = count + 1
        page_url = get_url(store)
        log.debug(f"{count}. scrapping {page_url} ...")
        if "locations/home" in page_url:
            count = count - 1
            continue
        store_number = MISSING

        location_type_check = get_JSON_object_variable_type(store, "isNew")
        if location_type_check is False:
            location_type = MISSING
        else:
            location_type = "Coming Soon"

        location_name = get_JSON_object_variable(store, "title")
        street_address = get_JSON_object_variable(
            store, "address.address1"
        ) + get_JSON_object_variable(store, "address.address2")
        street_address = street_address.replace(MISSING, " ").strip()
        city = get_JSON_object_variable(store, "address.city")
        zip_postal = get_JSON_object_variable(store, "address.zip")
        state = get_JSON_object_variable(store, "address.state")
        country_code = "US"
        phone = get_JSON_object_variable(store, "phone.0.value")
        latitude = get_JSON_object_variable(store, "coordinates.latitude")
        longitude = get_JSON_object_variable(store, "coordinates.longitude")
        hours_of_operation = get_hoo(page_url)

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

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
            raw_address=raw_address,
        )


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
