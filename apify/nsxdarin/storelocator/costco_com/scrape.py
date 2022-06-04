from lxml import html
from urllib.parse import urlparse
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

logger = SgLogSetup().get_logger("costco_com")
MISSING = SgRecord.MISSING
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}
BASE_URL = "https://www.costco.com"


@retry(stop=stop_after_attempt(10))
def fetch_loc(http, loc):
    return http.get(loc, headers=headers)


@retry(stop=stop_after_attempt(10))
def fetch_json_data(http, loc):
    r = http.get(loc, headers=headers)
    if r.text:
        data_json = json.loads(r.text)
        return data_json


def get_us_ca_store_urls(http):
    locs = []
    sitemap_urls = [
        "https://www.costco.com/sitemap_l_001.xml",
        "https://www.costco.ca/sitemap_l_001.xml",
    ]
    for url in sitemap_urls:
        r2 = fetch_loc(http, url)
        for raw_line in r2.iter_lines():
            line = str(raw_line)
            if (
                "<loc>https://www.costco.com/warehouse-locations/" in line
                or "<loc>https://www.costco.ca/warehouse-locations/" in line
            ):
                locs.append(line.split("<loc>")[1].split("<")[0])
    return locs


def get_global_urls(http):
    r1 = fetch_loc(http, BASE_URL)
    sel1 = html.fromstring(r1.text)
    lis = sel1.xpath('//div[contains(@id, "country-select")]/ul/li')
    country_and_url = []
    for li in lis:
        curl = "".join(li.xpath("./a/@href"))
        cname = "".join(li.xpath("./a/text()"))
        country_and_url.append((curl, cname))

    # The first 2 countries taken off from country_and_url list
    country_and_url = country_and_url[2:]
    logger.info(f"List of Countries: {country_and_url}")
    return country_and_url


def fetch_records(http: SgRequests):

    # This section scrapes the data for US and CA
    locs = get_us_ca_store_urls(http)
    for idx, loc in enumerate(locs[0:]):
        warehouse_number = loc.split("-")[-1].replace(".html", "")
        api_endpoint_url = f"https://www.costco.com/AjaxWarehouseBrowseLookupView?langId=-1&storeId=10301&numOfWarehouses=&hasGas=&hasTires=&hasFood=&hasHearing=&hasPharmacy=&hasOptical=&hasBusiness=&hasPhotoCenter=&tiresCheckout=0&isTransferWarehouse=false&populateWarehouseDetails=true&warehousePickupCheckout=false&warehouseNumber={warehouse_number}&countryCode="
        data = fetch_json_data(http, api_endpoint_url)
        data = data[1]

        # locator_domain
        locator_domain = "costco.com"
        logger.info(f"[{idx}] domain: {locator_domain}")

        # Page URL
        page_url = loc
        logger.info(f"[{idx}] purl: {page_url}")

        # Location Name
        locname = data["locationName"]
        location_name = locname if locname else MISSING
        logger.info(f"[{idx}] Locname: {location_name}")

        # Street Address
        street_address = data["address1"]
        street_address = street_address if street_address else MISSING
        logger.info(f"[{idx}] st_add: {street_address}")

        city = data["city"] if data["city"] else MISSING
        logger.info(f"[{idx}] city: {city}")

        state = data["state"] if data["state"] else MISSING
        logger.info(f"[{idx}] state: {state}")

        zip_postal = data["zipCode"] if data["zipCode"] else MISSING
        logger.info(f"[{idx}] zip: {zip_postal}")

        country_code = data["country"] if data["country"] else MISSING
        logger.info(f"[{idx}] country_code: {country_code}")

        store_number = data["stlocID"] if data["stlocID"] else MISSING
        logger.info(f"[{idx}] store_number: {store_number}")

        phone = " ".join(data["phone"].split())
        phone = phone if phone else MISSING
        logger.info(f"[{idx}] Phone: {phone}")

        # Location Type
        location_type = "Warehouse"
        logger.info(f"[{idx}] location_type: {location_type}")

        latitude = data["latitude"] if data["latitude"] else MISSING
        logger.info(f"[{idx}] lat: {latitude}")

        longitude = data["longitude"] if data["longitude"] else MISSING
        logger.info(f"[{idx}] long: {longitude}")

        warehouse_hoo = data["warehouseHours"]
        hours_of_operation = ""
        if warehouse_hoo:
            hours_of_operation = "; ".join(warehouse_hoo)
        else:
            hours_of_operation = MISSING
        logger.info(f"[{idx}] hoo: {hours_of_operation}")

        raw_address = MISSING
        logger.info(f"[{idx}] raw_add: {raw_address}")
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

    # The section scrapes the data for UK, MX, KR, TW, JP, AU, IS, FR, ES, and NZ
    # However, at this point of time, the data for New Zealand is not available
    global_url_wout_us_ca = get_global_urls(http)
    for urlpartnum, urlpart in enumerate(global_url_wout_us_ca[0:]):
        space_rep_w_plus = urlpart[1].replace(" ", "+")
        global_api_endpoint_url_formed = (
            f"{urlpart[0]}/store-finder/search?q={space_rep_w_plus}&page=0"
        )
        logger.info(f"Pulling the data from: {global_api_endpoint_url_formed}")
        global_data = fetch_json_data(http, global_api_endpoint_url_formed)
        if global_data is not None:
            global_data = global_data["data"]
            for idx1, gitem in enumerate(global_data[0:]):
                # locator_domain
                locator_domain = "costco.com"
                logger.info(f"[{idx1}] domain: {locator_domain}")

                # Page URL
                page_url = global_api_endpoint_url_formed
                page_url = page_url if page_url else MISSING
                logger.info(f"[{idx1}] purl: {page_url}")

                # Location Name
                locname = gitem["name"]
                location_name = locname if locname else MISSING
                logger.info(f"[{idx1}] Locname: {location_name}")

                # Street Address
                street_address = ""
                line1 = gitem["line1"]
                line2 = gitem["line2"]
                if line1 and line2:
                    street_address = line1 + ", " + line2
                elif line1 and not line2:
                    street_address = line1
                elif not line1 and line2:
                    street_address = line2
                else:
                    street_address = MISSING
                logger.info(f"[{idx1}] st_add: {street_address}")

                city = gitem["town"]
                city = city if city else MISSING
                logger.info(f"[{idx1}] city: {city}")

                state = ""
                state = state if state else MISSING
                logger.info(f"[{idx1}] state: {state}")

                zip_postal = gitem["postalCode"]
                zip_postal = zip_postal if zip_postal else MISSING
                logger.info(f"[{idx1}] zip: {zip_postal}")

                country_code = ""
                domain = urlparse(global_api_endpoint_url_formed).netloc
                cc = domain.split(".")[-1].upper()
                country_code = cc
                if country_code == "UK":
                    country_code = "GB"
                logger.info(f"[{idx1}] country_code: {country_code}")

                store_number = gitem["warehouseCode"]
                store_number = store_number if store_number else MISSING
                logger.info(f"[{idx1}] store_number: {store_number}")

                phone = gitem["phone"]
                phone = " ".join(phone.split())
                phone = phone if phone else MISSING
                logger.info(f"[{idx1}] Phone: {phone}")

                # Location Type
                location_type = "Warehouse"
                logger.info(f"[{idx1}] location_type: {location_type}")

                lat = gitem["latitude"]
                latitude = lat if lat else MISSING
                logger.info(f"[{idx1}] lat: {latitude}")

                lng = gitem["longitude"]
                longitude = lng if lng else MISSING
                logger.info(f"[{idx1}] long: {longitude}")

                warehouse_hoo = ""
                hours_of_operation = ""
                hoo = []
                if "openings" in gitem:
                    warehouse_hoo = gitem["openings"]
                    if warehouse_hoo:
                        for k, v in warehouse_hoo.items():
                            if "individual" in v:
                                times = v["individual"]
                                daytimes = k + " " + times
                                hoo.append(daytimes)
                        hours_of_operation = "; ".join(hoo)
                    else:
                        hours_of_operation = MISSING
                else:
                    hours_of_operation = MISSING
                logger.info(f"[{idx1}] hoo: {hours_of_operation}")

                raw_address = MISSING
                logger.info(f"[{idx1}] raw_add: {raw_address}")
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
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
