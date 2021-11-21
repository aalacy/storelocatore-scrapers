from sgpostal.sgpostal import parse_address_intl
import re
from lxml import html
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "www.aldoshoes.me"
website = "https://www.aldoshoes.me"
MISSING = SgRecord.MISSING
store_pages = [
    {"id": 30, "url": "/ae/en/stores"},
    {"id": 28, "url": "/kw/en/stores"},
    {
        "id": 32,
        "url": "/qa/en/stores",
    },
    {"id": 30, "url": "/om/en/stores"},
]
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def id_from_url(url):
    parts = url.split("/")
    return parts[len(parts) - 1]


def stringify_children(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            if text:
                values.append(text.strip())
    if len(values) == 0:
        return MISSING
    return " ".join(values)


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"\d+", Source):
        if len(match) > 5:
            phone = match
            return phone
    return phone


def get_js_object(response, varName, noVal=MISSING):
    parts = response.split(f"var {varName} = ")[1].split(";")[0]
    return parts


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_stores():
    store_urls = []
    for store_page in store_pages:
        ids = []
        response = request_with_retries(f"{website}{store_page['url']}")

        body = html.fromstring(response.text, "lxml")
        urls = body.xpath(
            '//div[contains(@class, "store-detail")]/a[contains(@class, "action view")]/@href'
        )

        for url in urls:
            id = id_from_url(url)
            ids.append(id)
            s_url = f"{website}{store_page['url']}/index/view/id/{id}"
            if s_url not in store_urls:
                store_urls.append(s_url)

        while True:
            found_new = False
            last_id = ids[len(ids) - 1]
            json_url = f"{website}{store_page['url']}/index/index/"
            payload = (
                f"id={last_id}&storefilter=Our+Stores&mainstoreid={store_page['id']}"
            )
            try:
                response = session.post(json_url, headers=headers2, data=payload)
                data = json.loads(response.text)
            except Exception as e:
                log.info(f"Data Err: {e}")
                data = []
            for sData in data:
                id = sData["storesid"]
                if id in ids:
                    continue
                found_new = True
                ids.append(id)
                s_url = f"{website}{store_page['url']}/index/view/id/{id}"
                if s_url not in store_urls:
                    store_urls.append(s_url)
            if not found_new:
                break
        log.debug(f"after {store_page['url']} stores= {len(store_urls)}")

    return store_urls


def fetch_data():
    store_urls = fetch_stores()
    log.info(f"Total stores = {len(store_urls)}")
    count = 0
    for page_url in store_urls:
        count = count + 1
        log.debug(f"{count}. Fetching {page_url} ...")
        location_type = "Store"
        response = request_with_retries(page_url)
        store_number = id_from_url(page_url)

        body = html.fromstring(response.text, "lxml")
        location_name = stringify_children(
            body, '//div[contains(@class, "store-name")]'
        )
        raw_address = stringify_children(
            body, '//div[contains(@class, "store-address")]/p'
        )
        phone = get_phone(raw_address)
        raw_address = (
            raw_address.replace(phone, "").replace("+968", "").replace("+", "").strip()
        )
        latitude = get_js_object(response.text, "lat")
        longitude = get_js_object(response.text, "lng")
        street_address, city, state, zip_postal = get_address(raw_address)
        country_code = page_url.replace(
            f"/en/stores/index/view/id/{store_number}", ""
        ).split("/")
        country_code = country_code[len(country_code) - 1].upper()
        hours_of_operation = stringify_children(
            body,
            '//div[contains(@class, "store-hours")]/div[contains(@class, "store-address")]/span',
        )

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
    return []


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
