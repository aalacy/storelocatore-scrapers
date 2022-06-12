# -*- coding: UTF-8 -*-

from urllib.parse import urlparse
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import html as ht

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "sephora.bh"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("sephora_bh")  # noqa

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}
MAX_WORKERS = 5

LOCATION_URLS_GRID = ["https://www.sephora.bh/bh/en/store"]


# Middle East
# These new store locators added.
# The stores in these locators used to be available un AE domain.
middle_east_store_locators = [
    "https://www.sephora.sa/en/store",
    "https://www.sephora.qa/qa/en/store",
    "https://www.sephora.com.kw/kw/en/store",
    "https://www.sephora.bh/bh/en/store",
    "https://www.sephora.ae/en/store",
    "https://www.sephora.om/om/en/store",
]  # Informational

logger.info(f"Middle East Store Locators: {middle_east_store_locators}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")  # noqa
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_store_urls():
    store_urls = []
    for gunum, gurl in enumerate(LOCATION_URLS_GRID[0:]):
        r = get_response(gurl)
        sel = html.fromstring(r.text, "lxml")
        purls = sel.xpath('//a[contains(@class, "store-name")]/@href')
        logger.info(f"Pulling the store URLs from: {gurl}")  # noqa
        logger.info(f"{gurl} | Total number of Store URLs: {len(purls)}")  # noqa
        store_urls.extend(purls)
    return store_urls


def fetch_records(idx, store_url, sgw: SgWriter):
    try:
        phone = ""
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        hours_of_operation = ""

        logger.info(f"[{idx}] Pulling the data from: {store_url}")  # noqa
        rcz = get_response(store_url)
        sel_cz = html.fromstring(rcz.text, "lxml")
        dcz = sel_cz.xpath(
            '//script[contains(@type, "application/ld+json") and contains(text(), "streetAddress") or contains(text(), "paymentAccepted")]/text()'
        )
        dcz1 = "".join(dcz)
        dcz2 = " ".join(dcz1.split())
        data_json = json.loads(dcz2)
        domain = urlparse(store_url).netloc
        locator_domain = domain.replace("www.", "")
        page_url = store_url

        location_name = data_json["name"]
        location_name = location_name if location_name else MISSING
        if location_name == "-":
            location_name = MISSING
        if location_name == "0":
            location_name = MISSING
        if location_name == "00":
            location_name = MISSING
        if location_name == "000":
            location_name = MISSING
        if location_name == "0000":
            location_name = MISSING
        if location_name == "00000":
            location_name = MISSING
        if location_name == "000000":
            location_name = MISSING

        if "address" in data_json:
            add = data_json["address"]
            street_address = " ".join(add["streetAddress"].split())
            street_address = street_address if street_address else MISSING
            city = add["addressLocality"]
            city = city if city else MISSING
            state = state if state else MISSING
            zip_postal = add["postalCode"]
            zip_postal = zip_postal if zip_postal else MISSING
            if zip_postal == "-":
                zip_postal = MISSING
            if zip_postal == "0":
                zip_postal = MISSING
            if zip_postal == "00":
                zip_postal = MISSING
            if zip_postal == "000":
                zip_postal = MISSING
            if zip_postal == "0000":
                zip_postal = MISSING
            if zip_postal == "00000":
                zip_postal = MISSING
            if zip_postal == "000000":
                zip_postal = MISSING
        else:
            street_address = MISSING
            city = MISSING
            state = MISSING
            zip_postal = MISSING

        logger.info(f"[{idx}] Zip Code: {zip_postal}")  # noqa

        # Street Address has additional info which
        # should be removed.
        street_address = " ".join(street_address.split())
        sta_sp = street_address.split(",")
        sta_additional_info_rmved = ""
        if len(sta_sp) > 1:
            sta_additional_info_rmved = sta_sp[0] + ", " + sta_sp[1]
        else:
            sta_additional_info_rmved = street_address
        if (
            "Al Badee District،، Riyadh 14924,  Saudi Arabia"
            in sta_additional_info_rmved
        ):
            sta_additional_info_rmved = "Al Badee District, Riyadh 14924"

        if sta_additional_info_rmved == "0":
            sta_additional_info_rmved = MISSING

        country_code = locator_domain.split(".")[-1].upper()
        store_number = page_url.split("storeID=")[-1]

        if "telephone" in data_json:
            phone = data_json["telephone"]
            phone = phone if phone else MISSING
        else:
            phone = MISSING
        if phone == "0":
            phone = MISSING
        if phone == "00":
            phone = MISSING
        if phone == "000":
            phone = MISSING
        if phone == "0000":
            phone = MISSING
        if phone == "00000":
            phone = MISSING
        if phone == "000000":
            phone = MISSING

        logger.info(f"[{idx}] Phone: {phone}")  # noqa

        # Location Type
        location_type = data_json["@type"]
        location_type = location_type if location_type else MISSING

        # Latlng
        latlng = "".join(
            sel_cz.xpath(
                '//div[contains(@data-default-coordinates, "longitude")]/@data-coord'
            )
        )
        latitude = None
        longitude = None
        try:
            latlng1 = json.loads(latlng)
            # Latitude
            latitude = latlng1["lat"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] lat: {latitude}")  # noqa

            # Longitude
            longitude = latlng1["lng"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] lng: {longitude}")  # noqa
        except:
            latitude = MISSING
            longitude = MISSING

        hoo = data_json["openingHours"]
        if isinstance(hoo, list):
            hours_of_operation = ", ".join(hoo)
        else:
            hours_of_operation = hoo
        logger.info(f"HOO: {hours_of_operation}")  # noqa

        if str(hours_of_operation) == "Mo-Su ":
            hours_of_operation = MISSING

        if str(hours_of_operation) == "Mo-Su":
            hours_of_operation = MISSING

        # Raw Address
        raw_address = street_address
        raw_address = raw_address if raw_address else MISSING
        if raw_address == "-":
            raw_address = MISSING
        if raw_address == "0":
            raw_address = MISSING
        if raw_address == "00":
            raw_address = MISSING
        if raw_address == "000":
            raw_address = MISSING
        if raw_address == "0000":
            raw_address = MISSING
        if raw_address == "00000":
            raw_address = MISSING
        if raw_address == "000000":
            raw_address = MISSING

        # Clean and making unsescaped for Germany's address
        # "D&uuml;sseldorf" needs to be transformed to Düsseldorf
        if country_code == "DE":
            raw_address = raw_address.split("+")[0].strip()
            raw_address = ht.unescape(raw_address)
            location_name = ht.unescape(location_name)
            sta_additional_info_rmved = sta_additional_info_rmved.split("+")[0].strip()
            sta_additional_info_rmved = ht.unescape(sta_additional_info_rmved)
            city = ht.unescape(city)

        if country_code == "CZ":
            raw_address = ht.unescape(raw_address)
            sta_additional_info_rmved = ht.unescape(sta_additional_info_rmved)
            city = ht.unescape(city)

        if country_code in ["ES", "DK", "FR", "SE", "PT", "PL", "IT"]:
            raw_address = ht.unescape(raw_address)
            location_name = ht.unescape(location_name)
            sta_additional_info_rmved = ht.unescape(sta_additional_info_rmved)
            city = ht.unescape(city)

        idx += 1
        item = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=sta_additional_info_rmved,
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
    except Exception as e:
        raise Exception(
            f" [{idx}] Please fix this >> {e} >> Error Encountered at {store_url}"
        )


def fetch_data(sgw: SgWriter):
    page_urls = get_store_urls()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx, store_url, sgw)
            for idx, store_url in enumerate(page_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
