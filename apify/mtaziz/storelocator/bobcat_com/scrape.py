from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MAX_WORKERS = 16
logger = SgLogSetup().get_logger("bobcat_com")
MISSING = SgRecord.MISSING
DOMAIN = "bobcat.com"


headers2 = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "AWSELB=6B314F9D18F97B28A1EE40CD414BA827E22AC87E154FD354CB5EC0AE5FF0845806B10CCED642D25A24DF2627581562372A35396705E3968742A120D70CB56AA52BED66FDA3; AWSELBCORS=6B314F9D18F97B28A1EE40CD414BA827E22AC87E154FD354CB5EC0AE5FF0845806B10CCED642D25A24DF2627581562372A35396705E3968742A120D70CB56AA52BED66FDA3; CookiePolicy=true",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers2)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_records(latlng, sgw: SgWriter):
    poilat, poilon = latlng
    api_base_url = "https://bobcat.know-where.com/bobcat/cgi/selection?"
    options = "option="
    api_endpoint_url = f"{api_base_url}{options}&ll={poilat}%2C{poilon}&lang=en&stype=ll&async=results&key"
    logger.info(f"Pulling the data from {api_endpoint_url}")

    rt = get_response(api_endpoint_url)

    # Check if requests gets through, if so then we can check if there is any data for the store
    logger.info(f"status: {rt.status_code}")
    selt = html.fromstring(rt.text, "lxml")
    kw_search_status = selt.xpath('//script[@id="kwSearchStatus"]/text()')
    kw_search_status = "".join(kw_search_status)
    logger.info(f"KW Search Status: {kw_search_status}")
    if "0 locations in your area" in kw_search_status:
        logger.info("No locations found in your area! :(")
        return
    else:
        trs = selt.xpath('//div[@id="kwresults-div"]/table/tr')
        for idx, tr in enumerate(trs):
            locator_domain = DOMAIN

            # Page URL
            page_url = tr.xpath('.//a[contains(@onclick, "Visit Website")]/@onclick')
            page_url = "".join(page_url)
            if page_url:
                try:
                    page_url = (
                        page_url.strip("'")
                        .strip("'")
                        .split("this.href=")[-1]
                        .lstrip("'")
                    )
                except:
                    page_url = MISSING
            else:
                page_url = MISSING
            logger.info(f"[{idx}] page_url: {page_url} | {len(page_url)}")

            location_name = tr.xpath(".//h4/text()")
            location_name = "".join((location_name))
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] location_name: {location_name}")

            raw_address_ = tr.xpath('.//td/div/div/span[@onclick=""]/div/text()')
            raw_address_ = "".join(raw_address_)
            logger.info(f"[{idx}]  Raw Address To be Parsed: {raw_address_}")
            pai = parse_address_intl(raw_address_)
            logger.info(f"[{idx}] Parsed Address: {pai}")

            street_address = pai.street_address_1
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = pai.city
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = pai.state
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = pai.postcode
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            country_code = ""
            if " " in zip_postal:
                country_code = "CA"
            else:
                country_code = "US"

            store_number = tr.xpath(
                './/span[contains(@id, "kw-view-product-line")]/@id'
            )
            store_number = "".join(store_number)
            try:
                store_number = store_number.split("-")[-1]
            except:
                store_number = MISSING

            phone = tr.xpath(
                './/div[@class="kw-result-link-container"]/a[contains(@onclick, "Phone Number")]/text()'
            )
            phone = "".join(phone)
            phone = phone if phone else MISSING
            logger.info(f"[{idx}]  Phone: {phone}")

            # Location Type
            location_type = ""
            location_type = location_type if location_type else MISSING

            # Latitude
            latitude = ""
            latitude = latitude if latitude else MISSING

            # Longitude
            longitude = ""
            longitude = longitude if longitude else MISSING
            hours_of_operation = MISSING

            # Raw Address
            raw_address = ""
            if raw_address_:
                raw_address = raw_address_
            else:
                raw_address = MISSING
            rec = SgRecord(
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
            sgw.write_row(rec)


def fetch_data(sgw: SgWriter):

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []

        search_us = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA],
            granularity=Grain_8(),
            expected_search_radius_miles=50,
            use_state=False,
        )
        task_us = [executor.submit(fetch_records, latlng, sgw) for latlng in search_us]

        tasks.extend(task_us)
        search_ca = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA],
            granularity=Grain_8(),
            expected_search_radius_miles=100,
            use_state=False,
        )
        task_ca = [executor.submit(fetch_records, latlng, sgw) for latlng in search_ca]
        tasks.extend(task_ca)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
