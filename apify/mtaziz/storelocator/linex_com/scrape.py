from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("linex_com")
DOMAIN = "linex.com"
MISSING = SgRecord.MISSING
LOCATOR_URL = "https://linex.com/find-a-location"
MAX_WORKERS = 10

headers_csrf = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "referer": "https://linex.com/find-a-location",
    "content-type": "multipart/form-data",
    "cookie": "_clck=1tuc36s|1|exj|0;",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_csrf(url, headers_c):
    with SgRequests() as http:
        response = http.get(url, headers=headers_c)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_csrf_token():
    r_csrf = get_response_csrf(LOCATOR_URL, headers_csrf)
    sel_csrf = html.fromstring(r_csrf.text, "lxml")
    csrf_token = sel_csrf.xpath('//meta[contains(@name, "csrf-token")]/@content')[0]
    logger.info(f"CSRF TOKEN: {csrf_token}")
    return csrf_token


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_post(payload, headers_p):
    with SgRequests() as http:
        r1 = http.post(LOCATOR_URL, data=json.dumps(payload), headers=headers_p)
        if r1.status_code == 200:
            logger.info(f"HTTP Status Code: {r1.status_code}")
            return r1
        raise Exception(
            f"{LOCATOR_URL} | {payload} >> HTTP Error Code: {r1.status_code}"
        )


def fetch_records(
    search_zipcode, current_country, csrf_token, headers_post, sgw: SgWriter
):
    payload = None
    logger.info(
        f"Pulling the data for the zipcode: {search_zipcode} | [{current_country}]"
    )

    if "us" in current_country:
        payload = {
            "_token": csrf_token,
            "country": "US",
            "location": search_zipcode,
            "country_intl": "",
        }

    if "ca" in current_country:
        payload = {
            "_token": csrf_token,
            "country": "CA",
            "location": search_zipcode,
            "country_intl": "canada",
        }

    r = get_response_post(payload, headers_post)
    code_dom = html.fromstring(r.text, "lxml")
    all_locations = code_dom.xpath('//div[@class="find-result "]')
    try:
        for idx2, loc_html in enumerate(all_locations[0:]):
            page_url = loc_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
            page_url = (
                "".join(page_url).replace(" ", "").replace("http://https", "https")
            )
            page_url = "".join(page_url.split())
            page_url = page_url if page_url else MISSING
            logger.info(f"[{search_zipcode}] [{idx2}] Page URL: {page_url}")

            # Location Name
            location_name = "".join(loc_html.xpath("./@data-title"))
            location_name = location_name if location_name else MISSING

            location_name_csoon = "".join(loc_html.xpath(".//h4//text()"))
            location_name_csoon = " ".join(location_name_csoon.split())
            logger.info(f"[{idx2}] Location Name Coming Soon: {location_name_csoon}")

            # Address Raw
            address_raw = loc_html.xpath(".//address/text()")
            address_raw = [elem.strip() for elem in address_raw if elem.strip()]
            street_address = ""
            city = ""
            state = ""
            zip_code = ""
            if len(address_raw[0]) == 1:
                street_address = MISSING
                city = MISSING
                state = MISSING
                zip_code = MISSING
            else:
                street_address = address_raw[0]
                city = address_raw[-1].split(",")[0].split()[:-1]
                city = " ".join(city) if city else MISSING
                state = address_raw[-1].split(",")[0].split()[-1:]
                state = state[0] if state else MISSING
                zip_code = address_raw[-1].split(",")[-1].strip()
            logger.info(f"{street_address} | {city} | {state} | {zip_code}")
            country_code = "US"
            if len(zip_code.split()) == 2:
                country_code = "CA"
            store_number = MISSING
            phone = loc_html.xpath(
                './/h5[contains(text(), "Contact:")]/following-sibling::p/text()'
            )
            phone = phone[0] if phone else MISSING
            logger.info(f"[{idx2}] Phone: {phone}")

            # Latlng
            latitude = "".join(loc_html.xpath("./@data-lat"))
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx2}] Latitude: {latitude}")

            longitude = "".join(loc_html.xpath("./@data-lon"))
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx2}] Longitude: {longitude}")

            location_type = MISSING
            hours_of_operation = ""

            hoo = loc_html.xpath('.//p[@class="hours"]/text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else MISSING

            if "coming soon" in location_name_csoon.lower():
                hours_of_operation = "Coming Soon"
            logger.info(f"[{idx2}] Hours of Operation: {hours_of_operation}")
            raw_address = MISSING
            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
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
    except Exception as e:
        logger.info(f"Fix the issue {e} at zip code of {search_zipcode}")


def fetch_data(sgw: SgWriter):
    SEARCH_RADIUS = 100
    all_codes_us = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=SEARCH_RADIUS,
    )

    all_codes_ca = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=SEARCH_RADIUS,
    )

    cn_us = all_codes_us.current_country()
    cn_ca = all_codes_ca.current_country()

    # It is noted that whether we use sgselenium or
    # sgrequests followed by POST,
    state_list_ca = [
        "ontario",
        "quebec",
        "british columbia",
        "alberta",
        "manitoba",
        "saskatchewan",
        "nova scotia",
        "new brunswick",
        "newfoundland and labrador",
        "prince edward island",
        "northwest territories",
        "nunavut",
        "yukon",
    ]
    state_list_us = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "newhampshire",
        "newjersey",
        "newmexico",
        "newyork",
        "northcarolina",
        "northdakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhodeisland",
        "southcarolina",
        "southdakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "westvirginia",
        "wisconsin",
        "wyoming",
        "District of Columbia",
    ]
    cn_us2 = "us"
    cn_ca2 = "ca"
    # Get CSRF Token
    CSRF_TOKEN = get_csrf_token()
    headers_post = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "referer": "https://linex.com/find-a-location",
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryV5hSBWKKKpSgeMjG",
    }

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []

        # Dynamic Zip Code-based search in the US
        task_us = [
            executor.submit(
                fetch_records, postcode, cn_us, CSRF_TOKEN, headers_post, sgw
            )
            for postcode in all_codes_us
        ]
        tasks.extend(task_us)

        # Dynamic Zip Code-based search in Canada
        task_ca = [
            executor.submit(
                fetch_records, postcode, cn_ca, CSRF_TOKEN, headers_post, sgw
            )
            for postcode in all_codes_ca
        ]
        tasks.extend(task_ca)

        # States in the US
        task_state_us = [
            executor.submit(
                fetch_records, postcode, cn_us2, CSRF_TOKEN, headers_post, sgw
            )
            for postcode in state_list_us
        ]
        tasks.extend(task_state_us)

        # Province in Canada
        task_state_ca = [
            executor.submit(
                fetch_records, postcode, cn_ca2, CSRF_TOKEN, headers_post, sgw
            )
            for postcode in state_list_ca
        ]
        tasks.extend(task_state_ca)

        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
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
