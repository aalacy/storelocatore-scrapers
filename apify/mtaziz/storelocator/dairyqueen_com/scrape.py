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
MAX_WORKERS = 10
DOMAIN = "dairyqueen.com"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def get_store_urls():
    store_urls = []
    sitemap_urls = [
        "https://www.dairyqueen.com/en-ca/sitemap.xml",
        "https://www.dairyqueen.com/en-us/sitemap.xml",
    ]
    for idx, url in enumerate(sitemap_urls):
        r = get_response(idx, url)
        logger.info(f"Pulling Store URLs for: {url}")
        en_ca = "<loc>https://www.dairyqueen.com/en-ca/locations/"
        en_us = "<loc>https://www.dairyqueen.com/en-us/locations/"
        ca_loc = "-ca/locations/</loc>"
        us_loc = "-us/locations/</loc>"
        for line in r.iter_lines():
            line = str(line)
            if (en_ca in line and ca_loc not in line) or (
                en_us in line and us_loc not in line
            ):
                store_urls.append(line.split("<loc>")[1].split("<")[0])
    return store_urls


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def fetch_records_us(idx, url, sgw: SgWriter):
    r = get_response(idx, url)
    s = html.fromstring(r.text, "lxml")
    data = s.xpath('//script[contains(@id, "__NEXT_DATA__")]/text()')
    data_json = json.loads("".join(data))
    contentletdata = data_json["props"]["pageProps"]["contentletData"]
    key = "".join(list(contentletdata.keys()))
    data = contentletdata[key]
    locator_domain = DOMAIN

    # Page URL
    page_url = data["urlTitle"]
    if page_url:
        page_url = "https://www.dairyqueen.com" + page_url
    else:
        page_url = MISSING

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

    store_number = data["storeId"]

    phone = data["phone"]
    phone = phone if phone else MISSING

    # Location Type
    location_type = data["conceptType"]
    location_type = location_type if location_type else MISSING

    # Latitude
    latitude = data["latlong"].split(",")[0].strip()
    latitude = latitude if latitude else MISSING

    # Longitude
    longitude = data["latlong"].split(",")[1].strip()
    longitude = longitude if longitude else MISSING

    hours_of_operation = ""
    try:
        hoo = data["miniSite"]
        if hoo is None:
            hours_of_operation = MISSING
        else:
            hoo1 = hoo["miniSiteHours"]
            hoo2 = hoo1.split(",")
            hoo3 = [i[:2] + " " + i[2:] for i in hoo2]
            hoo4 = [
                i.replace("1: ", "Sun: ")
                .replace("2: ", "Mon: ")
                .replace("3: ", "Tue: ")
                .replace("4: ", "Wed: ")
                .replace("5: ", "Thu: ")
                .replace("6: ", "Fri: ")
                .replace("7: ", "Sat: ")
                for i in hoo3
            ]

            d = {}
            for i in hoo4:
                k = i.split(" ")[0].replace(":", "")
                v = i.split(" ")[1]
                d[k] = v
            if "Sun" in d:
                sun = "Sun: " + d["Sun"]
            else:
                sun = "Sun: Closed"

            if "Mon" in d:
                mon = "Mon: " + d["Mon"]
            else:
                mon = "Mon: Closed"

            if "Tue" in d:
                tue = "Tue: " + d["Tue"]
            else:
                tue = "Tue: Closed"

            if "Wed" in d:
                wed = "Wed: " + d["Wed"]
            else:
                wed = "Wed: Closed"

            if "Thu" in d:
                thu = "Thu: " + d["Thu"]
            else:
                thu = "Thu: Closed"

            if "Fri" in d:
                fri = "Fri: " + d["Fri"]
            else:
                fri = "Fri: Closed"

            if "Sat" in d:
                sat = "Sat: " + d["Sat"]
            else:
                sat = "Sat: Closed"

            daytimes = [sun, mon, tue, wed, thu, fri, sat]
            hours_of_operation = "; ".join(daytimes)
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING
    except:
        hours_of_operation = MISSING

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


def fetch_data(sgw: SgWriter):
    store_urls = get_store_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, idx, url, sgw)
            for idx, url in enumerate(store_urls[0:])
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
