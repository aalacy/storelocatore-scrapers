from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from lxml import html
import json

logger = SgLogSetup().get_logger("dairyqueen_com")
MISSING = SgRecord.MISSING
MAX_WORKERS = 4
DOMAIN = "dairyqueen.com"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def get_store_urls():
    store_urls = []
    with SgRequests() as http:
        sitemap_urls = [
            "https://www.dairyqueen.com/en-ca/sitemap.xml",
            "https://www.dairyqueen.com/en-us/sitemap.xml",
        ]
        for url in sitemap_urls:
            r = http.get(url, headers=headers)
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


def fetch_records_us(idx, url, sgw: SgWriter):
    with SgRequests() as http:
        logger.info(f"pulling the data from: {url}")
        r = http.get(url, headers=headers)
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
        logger.info(f"[{idx}] page_url: {page_url} | {len(page_url)}")

        location_name = data["address1"]
        location_name = location_name if location_name else MISSING
        logger.info(f"[{idx}] location_name: {location_name}")

        street_address = data["address3"]
        street_address = street_address if street_address else MISSING
        logger.info(f"[{idx}] Street Address: {street_address}")

        city = data["city"]
        city = city if city else MISSING
        logger.info(f"[{idx}] City: {city}")

        state = data["stateProvince"]
        state = state if state else MISSING
        logger.info(f"[{idx}] State: {state}")

        zip_postal = data["postalCode"]
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"[{idx}] Zip Code: {zip_postal}")

        country_code = data["country"]
        country_code = country_code if country_code else MISSING

        store_number = data["storeId"]

        phone = data["phone"]
        phone = phone if phone else MISSING
        logger.info(f"[{idx}]  Phone: {phone}")

        # Location Type
        location_type = data["conceptType"]
        location_type = location_type if location_type else MISSING

        # Latitude
        latitude = data["latlong"].split(",")[0].strip()
        latitude = latitude if latitude else MISSING

        # Longitude
        longitude = data["latlong"].split(",")[1].strip()
        longitude = longitude if longitude else MISSING
        hoo = data["miniSite"]["miniSiteHours"]
        hoo1 = hoo.split(",")

        for dn, i in enumerate(hoo1):
            daytime = i[2:]
            if dn == 0:
                sun = "Sun: " + "" + daytime
            if dn == 1:
                mon = "Mon: " + "" + daytime
            if dn == 2:
                tue = "Tue: " + "" + daytime
            if dn == 3:
                wed = "Wed: " + "" + daytime
            if dn == 4:
                thu = "Thu: " + "" + daytime
            if dn == 5:
                fri = "Fri: " + "" + daytime
            if dn == 6:
                sat = "Sat: " + "" + daytime
        daytimes = [sun, mon, tue, wed, thu, fri, sat]
        hours_of_operation = "; ".join(daytimes)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        logger.info(f"[{idx}] HOO: {hours_of_operation}")

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
