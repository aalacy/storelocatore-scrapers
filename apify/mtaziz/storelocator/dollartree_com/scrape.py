from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed
import tenacity
from tenacity import retry, stop_after_attempt

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("dollartree_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

DOMAIN = "dollartree.com"
MISSING = SgRecord.MISSING
MAX_WORKERS = 5


# It is noted that when expected search radius miles is set to 100 miles along with granualrity ( Grain_8 ) -
# it returns 7915 records.
# It is also observed that with 100 miles radius, it returns 7915 records.
# Multiple times, it was tested with different settings and it max. returns 7915 records.


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response_post(url, data_body):
    with SgRequests() as http:
        logger.info(f"Pulling the data from: {url}")
        r = http.post(url, data=data_body, headers=headers)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{url} >> Temporary Error: {r.status_code}")


def fetch_records(zipcode, sgw: SgWriter):
    # Your scraper here
    location_url_state_city_with_hyphen_clientkey_part1_us = (
        "https://www.dollartree.com/locations/"
    )
    location_url_state_city_with_hyphen_clientkey_part1_ca = (
        "https://locations.dollartreecanada.com/"
    )
    start_url = (
        "https://hosted.where2getit.com/dollartree/rest/locatorsearch?lang=en_US"
    )

    body = '{"request":{"appkey":"134E9A7A-AB8F-11E3-80DE-744E58203F82","formdata":{"geoip":false,"dataview":"store_default","limit":1000,"order":"_DISTANCE","geolocs":{"geoloc":[{"addressline":"%s","country":"","latitude":"","longitude":""}]},"searchradius":"500","radiusuom":"","where":{"icon":{"eq":""},"ebt":{"eq":""},"freezers":{"eq":""},"crafters_square":{"eq":""},"snack_zone":{"eq":""},"distributioncenter":{"distinctfrom":"1"}},"false":"0"}}}'
    body_zipcode = body % zipcode
    logger.info(("Pulling zip Code %s..." % (zipcode)))
    response = get_response_post(start_url, body_zipcode)
    data = json.loads(response.text)
    if not data["response"].get("collection"):
        return
    logger.info(f'Stores found: {len(data["response"]["collection"])} at {zipcode}')
    for poi in data["response"]["collection"]:
        locator_domain = DOMAIN
        location_name = poi["name"]
        location_name = location_name if location_name else MISSING
        street_address = poi["address1"]
        street_address = street_address if street_address else MISSING

        # City
        city = poi["city"]

        # City name will be used to form the Page URL
        city_url = city.replace(" ", "-").lower()
        city = city if city else MISSING
        state = poi["state"]
        if not state:
            state = poi["province"]
        state_url = state.lower()
        state = state if state else MISSING
        zip_postal = poi["postalcode"]
        zip_postal = zip_postal if zip_postal else MISSING
        country_code = poi["country"]
        country_code = country_code if country_code else MISSING
        store_number = poi["clientkey"]

        # client key to be used to form the Page URL
        clientkey_url = store_number

        store_number = store_number if store_number else MISSING
        phone = poi["phone"]
        phone = phone if phone else MISSING
        location_type = MISSING
        location_type = location_type if location_type else MISSING
        latitude = poi["latitude"]
        latitude = latitude if latitude else MISSING
        longitude = poi["longitude"]
        longitude = longitude if longitude else MISSING
        hours_of_operation = poi["hours"]
        if poi["hours2"]:
            hours_of_operation += ", " + poi["hours2"]
        if not hours_of_operation:
            hours_of_operation = []
            for key, value in poi.items():
                if "hours" in key:
                    if not value:
                        continue
                    hours_of_operation.append(value)
            hours_of_operation = ", ".join(hours_of_operation)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        raw_address = poi["address1"]
        if poi.get("address2"):
            raw_address += " " + poi["address2"]
        if poi.get("address3"):
            raw_address += " " + poi["address3"]
        if country_code == "US":
            page_url = f"{location_url_state_city_with_hyphen_clientkey_part1_us}{state_url}/{city_url}/{clientkey_url}/"
        elif country_code == "CA":
            page_url = f"{location_url_state_city_with_hyphen_clientkey_part1_ca}{state_url}/{city_url}/{clientkey_url}/"
        else:
            page_url = MISSING

        item = SgRecord(
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
        sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    search_ca = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=500,
    )

    search_us = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_ca = [
            executor.submit(fetch_records, postcode, sgw) for postcode in search_ca
        ]
        tasks.extend(task_ca)
        task_us = [
            executor.submit(fetch_records, postcode, sgw) for postcode in search_us
        ]
        tasks.extend(task_us)

        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:

        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
