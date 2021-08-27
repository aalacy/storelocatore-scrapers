from sgrequests import SgRequests
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import json
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "levi.com"
logger = SgLogSetup().get_logger("levi_com")
MISSING = SgRecord.MISSING
GLOBAL_LOCATION_URL = "https://www.levi.com/GB/en_GB/store-finder/store-directory"
DOMAIN = "levi.com"
headers_custom = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def get_loc_urls():
    with SgRequests() as session:
        locs = []
        url = "https://locations.levi.com/sitemap.xml"
        r = session.get(url, headers=headers_custom)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if "<loc>https://locations.levi.com/en-" in line and ".html" in line:
                lurl = line.split(">")[1].split("<")[0]
                locs.append(lurl)
        return locs


def get_list_of_countries_global():
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get(GLOBAL_LOCATION_URL)
        driver.implicitly_wait(20)
        time.sleep(10)
        sel_driver = html.fromstring(driver.page_source, "lxml")
        list_of_country_codes = sel_driver.xpath(
            '//select[@id="storeDirectorySelect"]/option/@value'
        )
        list_of_country_codes = [lcc for lcc in list_of_country_codes if lcc]
        return list_of_country_codes


def get_custom_location_name(location_type, locname):
    location_name = None
    if location_type == "OUTLET":
        location_name = "Levi's Outlet"
    elif location_type == "RETAILER":
        location_name = "Levi's Retail Partner"
    elif location_type == "STORE":
        location_name = "Levi's Store"
    else:
        location_name = locname
    return location_name


def fetch_data_global():
    list_of_country_codes = get_list_of_countries_global()
    total = 0
    found = 0
    with SgRequests() as session:
        for countrynum, country_global in enumerate(list_of_country_codes[0:]):
            logger.info(f"Pulling data for the country code: {country_global}")
            API_ENDPOINT_URL = "https://www.levi.com/nextgen-webhooks/?operationName=storeDirectory&locale=GB-en_GB"
            PAYLOAD = {
                "operationName": "storeDirectory",
                "variables": {"countryIsoCode": country_global},
                "query": "query storeDirectory($countryIsoCode: String!) {\n  storeDirectory(countryIsoCode: $countryIsoCode) {\n    storeFinderData {\n      addLine1\n      addLine2\n      city\n      country\n      departments\n      distance\n      hrsOfOperation {\n        daysShort\n        hours\n        isOpen\n      }\n      latitude\n      longitude\n      mapUrl\n      phone\n      postcode\n      state\n      storeId\n      storeName\n      storeType\n      todaysHrsOfOperation {\n        daysShort\n        hours\n        isOpen\n      }\n      uom\n    }\n  }\n}\n",
            }
            response = session.post(
                API_ENDPOINT_URL, data=json.dumps(PAYLOAD), headers=headers_custom
            )
            if response.status_code == 200:
                data = response.json()
                found = len(data["data"]["storeDirectory"]["storeFinderData"])
                total += found
                for i in data["data"]["storeDirectory"]["storeFinderData"]:
                    location_name = i["storeName"] or MISSING
                    locator_domain = DOMAIN
                    page_url = MISSING
                    street_address = i["addLine1"] or MISSING
                    city = i["city"] or MISSING
                    state = i["state"] or MISSING
                    zip_postal = i["postcode"] or MISSING
                    country_code = i["country"] or MISSING
                    store_number = i["storeId"] or MISSING
                    phone = i["phone"] or MISSING
                    location_type = i["storeType"] or MISSING
                    location_name = get_custom_location_name(
                        location_type, location_name
                    )
                    latitude = i["latitude"] or MISSING
                    longitude = i["longitude"] or MISSING
                    hours_of_operation = ""
                    hrs_of_operation = i["hrsOfOperation"]
                    if hrs_of_operation:
                        hoo = []
                        for h in hrs_of_operation:
                            j = h["daysShort"] + " " + h["hours"]
                            hoo.append(j)
                        hours_of_operation = "; ".join(hoo)
                    else:
                        hours_of_operation = MISSING

                    addline1 = i["addLine1"]
                    addline2 = i["addLine2"]
                    city_raw = i["city"]
                    state_raw = i["state"]
                    zip_postal_raw = i["postcode"]
                    country_raw = i["country"]
                    raw_address = f"{addline1}, {addline2}, {city_raw}, {state_raw}, {zip_postal_raw}, {country_raw}"
                    raw_address = raw_address if raw_address else MISSING
                    yield SgRecord(
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
            logger.info(f"Found :{found}")

            logger.info(f"Total found: {total}")


def fetch_data_us_ca():
    loc_url_list = get_loc_urls()
    for idx, purl in enumerate(loc_url_list[0:]):
        with SgRequests() as session:
            r_row = session.get(purl, headers=headers_custom)
            sel_raw = html.fromstring(r_row.text, "lxml")
            data_ld_json = sel_raw.xpath(
                '//script[contains(@type, "application/ld+json")]/text()'
            )
            data_ld_json = "".join(data_ld_json)
            data_ld_json1 = data_ld_json.replace("'", " ")
            data_ld_json2 = " ".join(data_ld_json1.split())
            data_raw = (
                data_ld_json2.split("itemListElement")[0]
                .rstrip('"')
                .strip()
                .rstrip(", ")
                + "}}}]"
            )
            data = json.loads(data_raw)
            locator_domain = DOMAIN

            # Page URL
            page_url = purl
            logger.info(f"[{idx}] page_url: {page_url}")

            location_name = data[0]["name"]
            location_name = location_name.replace("<br/>", "")
            if location_name:
                location_name = location_name.strip()
            location_name = location_name.replace("Levi s®", "Levi's®")
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] location_name: {location_name}")

            street_address = data[0]["address"]["streetAddress"]
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = data[0]["address"]["addressLocality"]
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = data[0]["address"]["addressRegion"]
            state = state if state else MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = data[0]["address"]["postalCode"]
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            country_code = ""
            if "en-ca" in page_url:
                country_code = "CA"

            if "en-us" in page_url:
                country_code = "US"

            logger.info(f"[{idx}] country_code: {country_code}")

            store_number = page_url.split("_")[-1].replace(".html", "").strip()
            store_number = store_number if store_number else MISSING
            logger.info(f"[{idx}]  store_number: {store_number}")

            phone = data[0]["address"]["telephone"]
            phone = phone if phone else MISSING
            logger.info(f"[{idx}]  Phone: {phone}")

            # Location Type
            locname = location_name.lower()
            location_type = ""
            if "outlet" in locname:
                location_type = "OUTLET"
            elif "retailer" in locname:
                location_type = "RETAILER"
            elif "store" in locname:
                location_type = "STORE"
            else:
                location_type = location_name
            location_type = location_type if location_type else MISSING
            logger.info(f"[{idx}] location_type: {location_type}")

            # Custom Location Name
            location_name = get_custom_location_name(location_type, location_name)

            # Latitude
            latitude = data[0]["geo"]["latitude"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] lat: {latitude}")

            # Longitude
            longitude = data[0]["geo"]["longitude"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] lng: {longitude}")

            hours_of_operation = data[0]["openingHours"]
            logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

            # Raw Address
            raw_address = ""
            raw_address = raw_address if raw_address else MISSING
            yield SgRecord(
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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = list(fetch_data_global())
        data_us_ca = list(fetch_data_us_ca())
        results.extend(data_us_ca)
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
