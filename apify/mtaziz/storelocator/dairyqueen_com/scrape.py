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
import random
import time

logger = SgLogSetup().get_logger("dairyqueen_com")
MISSING = SgRecord.MISSING
MAX_WORKERS = 5
DOMAIN = "dairyqueen.com"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(180))
def get_response_json(idx, url):
    with SgRequests(verify_ssl=False) as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            try:
                sel = html.fromstring(response.text, "lxml")
                data_next = sel.xpath('//script[contains(@id, "__NEXT_DATA__")]/text()')
                data_json = json.loads("".join(data_next))
                logger.info(f"data json length: {len(data_json)}")
                return response
            except Exception as e:
                raise Exception(f"[{idx}] | {url} Fix <<{e}>>: {response.status_code}")
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_store_urls():
    store_urls_raw = []
    store_urls_list = []
    sitemap_urls = ["https://www.dairyqueen.com/en-us/sitemap.xml"]
    for idx, url in enumerate(sitemap_urls):
        r = get_response(idx, url)
        logger.info(f"Pulling Store URLs for: {url}")
        en_us = "<loc>https://www.dairyqueen.com/en-us/locations/"
        us_loc = "-us/locations/</loc>"
        for line in r.iter_lines():
            line = str(line)
            if en_us in line and us_loc not in line:
                store_urls_raw.append(line.split("<loc>")[1].split("<")[0])
    for i in store_urls_raw:
        length_of_forward_slash = len(i.split("/"))
        if length_of_forward_slash == 8:
            continue
        else:
            store_urls_list.append(i)
    return store_urls_list


def get_business_hoo(tstore_data):
    hours_of_operation = None
    try:
        hoo = tstore_data["minisite"]
        hours = hoo["hours"]
        hoo_business = []
        for i in hours:
            calendar_type = i["calendarType"]
            if calendar_type == "BUSINESS":
                ranges = i["ranges"]
                for r in ranges:
                    start = r["start"]
                    end = r["end"]
                    weekday = r["weekday"]
                    wd_start_end = f"{weekday} {start} - {end}"
                    hoo_business.append(wd_start_end)
        hours_of_operation = "; ".join(hoo_business)
    except:
        hours_of_operation = MISSING
    return hours_of_operation


def fetch_records_us(idx, url, sgw: SgWriter):
    try:
        r = get_response_json(idx, url)
        s = html.fromstring(r.text, "lxml")
        data = s.xpath('//script[contains(@id, "__NEXT_DATA__")]/text()')
        data_json = json.loads("".join(data))
        contentletdata = data_json["props"]["pageProps"]["contentletData"]
        key = "".join(list(contentletdata.keys()))
        data_key = contentletdata[key]
        data = data_key["storeData"]

        locator_domain = DOMAIN

        # Page URL
        page_url = url

        location_name = data["address1"]
        location_name = location_name if location_name else MISSING

        street_address = data["address3"]
        street_address = street_address if street_address else MISSING
        city = data["city"]
        city = city if city else MISSING
        state = data["stateProvince"]
        state = state if state else MISSING
        zip_postal = data["postalCode"]
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"[{idx}] | ZipCode: {zip_postal}")

        country_code = data["country"]
        country_code = country_code if country_code else MISSING

        store_number = data["storeNo"]

        phone = data["phone"]
        phone = phone if phone else MISSING

        # Location Type
        location_type = data["conceptType"]
        location_type = location_type if location_type else MISSING

        # Latitude
        latitude = data["latitude"]
        latitude = latitude if latitude else MISSING

        # Longitude
        longitude = data["longitude"]
        longitude = longitude if longitude else MISSING

        hours_of_operation = get_business_hoo(data)

        comingsoon_flag = data.get("flags")["comingSoonFlag"]
        if comingsoon_flag is True:
            hours_of_operation = "Coming Soon"

        temporarily_closed_flag = data.get("flags")["temporarilyClosedFlag"]
        if temporarily_closed_flag is True:
            hours_of_operation = "Temporarily Closed"

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
        return rec
    except Exception as e:
        logger.info(f"Please fix <<{e}>> for {idx} | {url}")


global round1_total_count
round1_total_count = 0
global success_page_urls_set1
success_page_urls_set1 = []
global store_urls
store_urls = []


def fetch_data1(sgw: SgWriter):
    global round1_total_count
    global success_page_urls_set1
    global store_urls
    logger.info("Crawling Store URLs")
    store_urls = get_store_urls()
    logger.info(f"Total Store count: {len(store_urls)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, idx, url, sgw)
            for idx, url in enumerate(store_urls[0:])
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            fr = future.result()
            # fr returns a dict with the data
            if fr is not None:
                success_page_urls_set1.append(fr.as_dict()["page_url"])
                sgw.write_row(fr)
                round1_total_count += 1


global success_page_urls_set2
success_page_urls_set2 = []

global round2_total_count
round2_total_count = 0

global second_round_of_try_store_urls
second_round_of_try_store_urls = []


def fetch_data2(sgw: SgWriter):

    global success_page_urls_set2
    global round2_total_count
    global second_round_of_try_store_urls
    global store_urls

    # Make a list which would contain the store URLs those failed in the first round
    for surl in store_urls:
        if surl not in success_page_urls_set1:
            second_round_of_try_store_urls.append(surl)
    logger.info("2nd round of Crawling Store URLs")
    logger.info(f"Total Store count 2nd Round: {len(second_round_of_try_store_urls)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, idx, url, sgw)
            for idx, url in enumerate(second_round_of_try_store_urls[0:])
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            fr = future.result()
            # fr returns a dict object with the data
            if fr is not None:
                success_page_urls_set2.append(fr.as_dict()["page_url"])
                sgw.write_row(fr)
                round2_total_count += 1


def scrape1():
    logger.info("Round1 Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data1(writer)
    logger.info("Round1 Finished")


# Second Round of Scraping.
# This is because, in the first round, some of the URls experience redirections
# and Retry does not fully to resolve the issue, therefore, 2nd attempt for those failed
# in the first round might be crawled with success.


def scrape2():
    logger.info("Round2 Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data2(writer)
    logger.info("Round2 Finished")


if __name__ == "__main__":
    scrape1()
    scrape2()
    logger.info(f"Round1 Total Count: {round1_total_count} out of {len(store_urls)}")
    logger.info(f"Round2 Total Count: {round2_total_count}")
    total_count = round1_total_count + round2_total_count
    logger.info(
        (f"Total store count from round1 & round2: {total_count} of {len(store_urls)} ")
    )
    problematic_stores_count = len(store_urls) - total_count
    logger.info(
        (f"Problematic stores count: {problematic_stores_count} of {len(store_urls)} ")
    )
    not_success_urls = []
    for ssurl in second_round_of_try_store_urls:
        if ssurl not in success_page_urls_set2:
            not_success_urls.append(ssurl)
    logger.info(f"UNSUCCESSFUL STORE URLs count: {len(not_success_urls)}")
    logger.info(f"UNSUCCESSFUL STORE URLs List: {not_success_urls}")
    logger.info("Scrape Finished")
