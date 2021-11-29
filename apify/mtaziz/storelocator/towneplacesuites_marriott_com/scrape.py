from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed
import tenacity
import json
import ssl
import time
import random

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "towneplacesuites.marriott.com"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"
logger = SgLogSetup().get_logger("towneplacesuites_marriott_com")

MAX_WORKERS = 4
MISSING = SgRecord.MISSING
headers_api = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}

# Marriott Hotels has total 30 brands.
# Note: Marriott Hotels ( MC ) contains MC and MV (Marriott Vacation Club) brands as well
# This contributes total 23 brands out of 30 brands
# There are 22 API_ENDPOINT URLs but it will return the data for 23 brands
# The rest of the 7 brands will be scraped using manual scraping method
# At the time of scraping total 23 brands contritubes store count 7642

url_api_endpoints_23_brands = {
    "https://ac-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_AR_en-US.json",
    "https://aloft-hotels.marriott.com/locations/": "https://pacsys.marriott.com/data/marriott_properties_AL_en-US.json",
    "https://autograph-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_AK_en-US.json",
    "https://courtyard.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_CY_en-US.json",
    "https://delta-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_DE_en-US.json",
    "https://design-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_DS_en-US.json",
    "https://element-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_EL_en-US.json",
    "https://fairfield.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_FI_en-US.json",
    "https://four-points.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_FP_en-US.json",
    "https://jw-marriott.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_JW_en-US.json",
    "https://marriott-hotels.marriott.com/locations/": "https://pacsys.marriott.com/data/marriott_properties_MC_en-US.json",
    "https://moxy-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_OX_en-US.json",
    "https://residence-inn.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_RI_en-US.json",
    "https://sheraton.marriott.com": "https://pacsys.marriott.com/data/marriott_properties_SI_en-US.json",
    "https://springhillsuites.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_SH_en-US.json",
    "https://le-meridien.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_MD_en-US.json",
    "https://the-luxury-collection.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_LC_en-US.json",
    "https://towneplacesuites.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_TS_en-US.json",
    "https://tribute-portfolio.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_TX_en-US.json",
    "https://w-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_WH_en-US.json",
    "https://westin.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_WI_en-US.json",
    "https://st-regis.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_XR_en-US.json",
}


def fetch_json_data(url, http: SgRequests):
    try:
        response = http.get(url, headers=headers_api)
        time.sleep(random.randint(7, 15))
        logger.info("JSON data being loaded...")
        response_text = response.text
        store_list = json.loads(response_text)
        data_regions = store_list["regions"]
        return data_regions
    except Exception as exception:
        logger.info(f"request {url} failed | {exception}")
        raise exception


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def fetch_data_for_23_child_brands_from_api_endpoints(
    url, http: SgRequests, sgw: SgWriter
):
    # This scrapes the data for 23 child brands
    brands_and_total_count_per_brand = []
    data_8 = fetch_json_data(url, http)
    found = 0
    for i in data_8:
        for j in i["region_countries"]:
            for k1 in j["country_states"]:
                for h in k1["state_cities"]:
                    for g in h["city_properties"]:
                        found += 1
                        locator_domain = DOMAIN
                        key = g["marsha_code"]
                        if key:
                            page_url = (
                                f"{'https://www.marriott.com/hotels/travel/'}{str(key)}"
                            )
                        else:
                            page_url = MISSING
                        logger.info(f"[Page URL: {page_url} ]")

                        # Location Name
                        location_name = g["name"]
                        location_name = location_name if location_name else MISSING

                        # Street Address
                        street_address = g["address"]
                        street_address = street_address if street_address else MISSING

                        # City
                        city = g["city"]
                        city = city if city else MISSING

                        # State
                        state = g["state_name"]
                        state = state if state else MISSING

                        # Zip Code
                        zip_postal = g["postal_code"]
                        zip_postal = zip_postal if zip_postal else MISSING

                        # Country Code
                        country_code = g["country_name"]
                        country_code = country_code if country_code else MISSING

                        # Store Number
                        store_number = MISSING

                        # Phone
                        phone = g["phone"]
                        phone = phone if phone else MISSING

                        # Location Type
                        location_type = g["brand_code"]
                        if location_type:
                            location_type = location_type + " " + "Hotels"
                        else:
                            location_type = MISSING
                        # Latitude
                        latitude = g["latitude"]
                        latitude = latitude if latitude else MISSING

                        # Longitude
                        longitude = g["longitude"]
                        longitude = longitude if longitude else longitude

                        # Number of Operations

                        hours_of_operation = ""
                        hours_of_operation = (
                            hours_of_operation if hours_of_operation else MISSING
                        )

                        # Raw Address
                        raw_address = ""
                        raw_address = raw_address if raw_address else MISSING

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

        total_count_per_brand = {"Brand Name": url, "Count": found}
    brands_and_total_count_per_brand.append(total_count_per_brand)
    logger.info(f"Counts for all brands: {brands_and_total_count_per_brand}")


def fetch_data(sgw: SgWriter, http: SgRequests):
    urls = []
    for k, v in url_api_endpoints_23_brands.items():
        urls.append(v)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                fetch_data_for_23_child_brands_from_api_endpoints, url, http, sgw
            )
            for url in urls
        ]
        for future in as_completed(futures):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            fetch_data(writer, http)
    logger.info("Scraping Finished")


if __name__ == "__main__":
    scrape()
