from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import cloudscraper
import os
from tenacity import retry, stop_after_attempt
import tenacity
import json
import ssl
import time
import random
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://www.1800packrat.com/locations"
DOMAIN = "1800packrat.com"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger(logger_name="1800packrat_com")


proxy_password = os.environ["PROXY_PASSWORD"]
DEFAULT_PROXY_URL = (
    f"http://groups-RESIDENTIAL,country-us:{proxy_password}@proxy.apify.com:8000/"
)
proxies = {
    "http": DEFAULT_PROXY_URL,
    "https": DEFAULT_PROXY_URL,
}  # Proxy that works with cloudscraper


def get_store_urls():
    try:
        response = get_response(LOCATION_URL)
        geo = dict()
        urls = []
        urls_latlng = []
        tree = html.fromstring(response.text, "lxml")
        logger.info(f"html content: {response.text}")
        text = (
            "".join(tree.xpath("//script[contains(text(), 'markers:')]/text()"))
            .split("markers:")[1]
            .split("]")[0]
            .strip()[:-1]
            + "]"
        )
        js = json.loads(text)
        for j in js:
            slug = j.get("Link")
            url = f"https://www.{DOMAIN}{slug}"
            urls.append(url)
            lat = j.get("Latitude") or MISSING
            lng = j.get("Longitude") or MISSING
            geo[slug] = {"lat": lat, "lng": lng}
            logger.info(f"Latitude & Longitude: {geo}")
            logger.info(f"List of Store URLs: {urls}")

        for k, v in geo.items():
            url = f"https://www.1800packrat.com{k}"
            lat = v["lat"]
            lng = v["lng"]
            z = (url, lat, lng)
            urls_latlng.append(z)

        return urls_latlng

    except Exception as e:
        logger.info(f" {e} >> Error getting from {LOCATION_URL}")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(10))
def get_response(url):
    scraper = cloudscraper.CloudScraper()
    response_proxy = scraper.get(url, proxies=proxies)
    time.sleep(random.randint(5, 15))
    if response_proxy.status_code == 200:
        logger.info(f"{url} >> HTTP Status: {response_proxy.status_code}")
        return response_proxy

    raise Exception(f"{url} >> Temporary Error: {response_proxy.status_code}")


def fetch_record(idx, url_latlng):
    store_url = url_latlng[0]
    try:
        response = get_response(store_url)
        time.sleep(random.randint(4, 7))
        logger.info(f"Pulling the data from {store_url}")
        page_sel = html.fromstring(response.text, "lxml")
        xpath_json_data = '//script[contains(@type, "application/ld+json") and contains(text(), "MovingCompany")]/text()'
        json_data = page_sel.xpath(xpath_json_data)
        logger.info(f"JSON Data: {json_data}")
        # All the data is not available in JSON form, therefore we need to parse using lxml
        if json_data:
            json_data = "".join(json_data)
            json_data = " ".join(json_data.split())
            json_data = json.loads(json_data)
            page_url = json_data["url"]
            location_name = json_data["name"] or MISSING
            address = json_data["address"]
            sa = address["streetAddress"] or MISSING
            street_address = sa
            city = address["addressLocality"] or MISSING
            state = address["addressRegion"] or MISSING
            zip_postal = address["postalCode"] or MISSING
            country_code = "US"
            store_number = MISSING
            phone = json_data["telephone"] or MISSING
            location_type = json_data["@type"]
            lat = url_latlng[1] or MISSING
            latitude = lat
            logger.info(f"[{idx}] Latitude: {lat}")
            lng = url_latlng[2] or MISSING
            longitude = lng
            logger.info(f"[{idx}] Longitude: {lng}")
            locator_domain = "1800packrat.com"

            # Hours of Operation
            hoo = []
            for i in json_data["openingHoursSpecification"]:
                day_of_week = (
                    i["dayOfWeek"].replace("http://schema.org/", "")
                    + " "
                    + str(i["opens"] or "")
                    + " - "
                    + str(i["closes"] or "")
                )
                hoo.append(day_of_week)
            hours_of_operation = "; ".join(hoo)
            logger.info(f"[{idx}] HOO: {hours_of_operation}")
            raw_address = MISSING

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
        else:
            location_name = "".join(page_sel.xpath("//title/text()"))
            location_name = (
                location_name.split("|")[-1]
                + ", "
                + location_name.split("|")[0].split(" in ")[-1]
            )
            location_name = location_name.strip() or MISSING
            logger.info(f"[{idx}] locname: {location_name}")

            page_url = store_url

            a = page_sel.xpath('//div[@class="location-info"]/div/p/text()')
            b = [" ".join(i.split()) for i in a]
            address_x = ", ".join(b[0:2])
            pai = parse_address_intl(address_x)
            street_address = pai.street_address_1
            city = pai.city or MISSING
            state = pai.state or MISSING
            zip_postal = pai.postcode or MISSING
            country_code = "US"
            store_number = MISSING
            phone = "".join(page_sel.xpath('//*[@class="nav-clickToCall"]/span/text()'))
            phone = phone if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            location_type = "MovingCompany"

            lat = url_latlng[1] or MISSING
            latitude = lat
            logger.info(f"[{idx}] Latitude: {lat}")

            lng = url_latlng[2] or MISSING
            longitude = lng
            logger.info(f"[{idx}] Longitude: {lng}")

            locator_domain = "1800packrat.com"
            hoo = page_sel.xpath(
                '//p[contains(text(), "CUSTOMER SERVICE HOURS")]//following-sibling::text()'
            )
            hoo1 = [" ".join(h.split()) for h in hoo]
            hoo1 = [h for h in hoo1 if h]
            hours_of_operation = None
            if hoo1:
                hours_of_operation = ", ".join(hoo1)
            else:
                hours_of_operation = MISSING

            logger.info(f"[{idx}] HOO: {hours_of_operation}")
            raw_address = address_x
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

    except Exception as e:
        raise Exception(f" {e} >> Error getting from {store_url}")


def scrape():
    urls_latlng = get_store_urls()
    count = 0
    logger.info("Started")

    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for idx, url_latlng in enumerate(urls_latlng[0:]):
            records = fetch_record(idx, url_latlng)
            for rec in records:
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
