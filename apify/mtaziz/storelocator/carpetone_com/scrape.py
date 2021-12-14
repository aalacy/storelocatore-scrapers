from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import json
from tenacity import retry, stop_after_attempt
import tenacity
from random import randint
import time


logger = SgLogSetup().get_logger("carpetone_com")
MISSING = SgRecord.MISSING
MAX_WORKERS = 6
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}
locator_domain_url = "carpetone.com"


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(2))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(randint(1, 4))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_store_urls_per_api_call(skip):
    urls = []
    api_url = f"https://www.carpetone.com/carpetone/api/Flooring/GetStores?map=true&zipcode=&latitude=45.7135097&longitude=-73.9859414&skip={skip}"
    response = get_response(skip, api_url)
    data = json.loads(response.text)
    logger.info(f"Pulling for [{skip}]")
    page_url = ""
    if data["Results"]:
        for _ in data["Results"]:
            if "PageUrl" in _:
                page_url = _["PageUrl"]
                if "https://" not in page_url:
                    page_url = "https://www.carpetone.com" + page_url
                urls.append(page_url)
    return urls


def get_store_urls_us_ca():
    store_urls = []
    s = set()
    with ThreadPoolExecutor(max_workers=6, thread_name_prefix="fetcher") as executor:
        futures = [
            executor.submit(get_store_urls_per_api_call, skip_num)
            for skip_num in range(0, 750)
        ]
        for fut in futures:
            try:
                for url in fut.result():
                    if url not in s:
                        store_urls.append(url)
                    s.add(url)
            except Exception as e:
                logger.info(f"Exception: {e}")
    return store_urls


def fetch_records(idx, url_store, sgw: SgWriter):
    try:

        logger.info(f"[{idx}] Pulling data from: {url_store}")
        r = get_response(idx, url_store)
        time.sleep(randint(2, 3))
        data_raw = html.fromstring(r.text, "lxml")
        data_xpath = '//script[contains(@type, "application/ld+json") and contains(text(), "openingHours")]/text()'
        data_type_json = data_raw.xpath(data_xpath)
        if data_type_json:
            data_type_json = "".join(data_type_json)
            data = json.loads(data_type_json)
            locator_domain = locator_domain_url
            page_url = data["url"] or MISSING
            location_name = "".join(data_raw.xpath("//title/text()"))
            location_name = location_name.split("|")[0] if location_name else MISSING
            data_address = data["address"]
            street_address = data_address["streetAddress"]
            street_address = street_address if street_address else MISSING
            city = data_address["addressLocality"] or MISSING
            state = data_address["addressRegion"] or MISSING
            country_code = data_address["addressCountry"] or MISSING
            zip_postal = data_address["postalCode"] or MISSING
            logger.info(
                f"[{idx}] STA: {street_address} | S: {state} | C: {city} | ZP: {zip_postal}"
            )
            store_number = MISSING
            store_number = store_number.strip() if store_number else MISSING
            phone_data = data["telephone"]
            phone = phone_data if phone_data else MISSING
            location_type = data["@type"] or MISSING
            try:
                hasmap = data["hasMap"]
                lat = hasmap.split("/")[-1].split(",")[0]
                latitude = lat if lat else MISSING
                lng = hasmap.split("/")[-1].split(",")[1]
                longitude = lng if lng else MISSING
            except:
                latitude = MISSING
                longitude = MISSING
            hoo = data["openingHours"]
            hours_of_operation = hoo if hoo else MISSING
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
        else:
            country_code = "CA" if "carpetone.ca" in url_store else "US"
            rec = SgRecord(
                locator_domain=locator_domain_url,
                page_url=url_store,
                location_name=MISSING,
                street_address=MISSING,
                city=MISSING,
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
                raw_address=MISSING,
            )
            sgw.write_row(rec)

    except Exception as e:
        logger.info(f"{url_store} is having issues, please fix it {e}!")


def fetch_data(sgw: SgWriter):
    all_urls = get_store_urls_us_ca()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records, idx, url, sgw)
            for idx, url in enumerate(all_urls[0:])
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
