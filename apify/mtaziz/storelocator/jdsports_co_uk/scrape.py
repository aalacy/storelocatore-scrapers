# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
from tenacity import retry, stop_after_attempt
import tenacity


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}

MAX_WORKERS = 6
logger = SgLogSetup().get_logger("tdsports_co_uk")


def format_store_locator_url():
    list_of_countries = """GB (here): jdsports.co.uk
                        ES: jdsports.es
                        SE: jdsports.se
                        BE: jdsports.be
                        AU: jd-sports.com.au
                        DE: jdsports.de
                        DK: jdsports.dk
                        SG: jdsports.com.sg
                        FR: jdsports.fr
                        FI: jdsports.fi
                        MY: jdsports.my
                        IT: jdsports.it
                        NL: jdsports.nl
                        TH: jdsports.co.th
                        AT: jdsports.at
                        PT: jdsports.pt
                        NZ: jdsports.co.nz"""
    lofc = list_of_countries.split("\n")
    lofc1 = [i.split(": ")[-1] for i in lofc]
    lofc_locator = [
        (
            "https://www." + i + "/store-locator/all-stores/",
            "https://www." + i,
            i,
            i.split(".")[-1].upper(),
        )
        for i in lofc1
    ]
    return lofc_locator


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_store(url):
    with SgRequests(proxy_country="gb") as http:
        response = http.get(url, headers=headers)
        logger.info(f"HTTPStatusCode: {response.status_code} | {url}")
        if response.status_code == 200:
            logger.info(f"{url} >> HTTPStatusCode: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTPErrorCode: {response.status_code}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_store_locator(url):
    with SgRequests(proxy_country="gb") as http:
        response = http.get(url, headers=headers)
        logger.info(f"HTTPStatusCode: {response.status_code} | {url}")
        if response.status_code == 200:
            logger.info(f"{url} >> HTTPStatusCode200 OK: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTPErrorCode: {response.status_code}")


def get_store_urls_per_country(all_stores_url, web, domain_name, country_name):
    r = get_response_store_locator(all_stores_url)
    logger.info(f"HTTPStatusCode: {r.status_code}")
    sel = html.fromstring(r.text, "lxml")
    links = sel.xpath('//li[contains(@data-e2e, "storeLocator-list-item")]/a/@href')
    links_full = []
    for link in links:
        new = web + link
        links_full.append((new, web, domain_name, country_name))
    return links_full


def get_store_urls_for_all_countries():
    all_locators = format_store_locator_url()
    all_country_store_urls = []
    for idx, i in enumerate(all_locators[0:]):
        all_stores_loc_url, website, domain, country = i
        logger.info(f"[{idx}] Pulling store urls for {country}")
        all_store_urls_per_country = get_store_urls_per_country(
            all_stores_loc_url, website, domain, country
        )
        all_country_store_urls.append(all_store_urls_per_country)
    return all_country_store_urls


def get_hours(js1):
    ohs = js1["openingHoursSpecification"]
    hoo = []
    for hnum, h in enumerate(ohs):
        dw = h["dayOfWeek"]
        o = h["opens"]
        c = h["closes"]
        dw_o_c = ""
        if not o and not c:
            dw_o_c = dw + " Closed"
        else:
            dw_o_c = dw + " " + o + " - " + c
        hoo.append(dw_o_c)
    hours_of_op = "; ".join(hoo)
    return hours_of_op


def fetch_records(storenum, store, sgw: SgWriter):
    # Store URL example data
    # Store URL - https://www.jdsports.co.uk/store-locator/as-gatwick-south/735/,
    # Website - https://www.jdsports.co.uk,
    # Domain - jdsports.co.uk,
    # Country - UK.
    store_url, site, domain, country = store
    logger.info(f"[{storenum}] PullingContentFrom: {store_url}")

    r_store = get_response_store(store_url)
    sel_store = html.fromstring(r_store.text, "lxml")
    data_raw = sel_store.xpath(
        '//script[contains(@type, "application/ld+json") and contains(text(), "Store")]/text()'
    )[0]
    data_raw_normalized = None
    # https://www.jdsports.fr/store-locator/la-seyne-sur-mer-chausport/1822/ experiences  JSON encoding error,
    # need to handle it separately.
    try:
        js = json.loads(data_raw)
    except:
        data_raw_normalized = " ".join(data_raw.split())
        js = json.loads(data_raw_normalized)

    DOMAIN = domain
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip_code = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    raw_address = ""
    page_url = js["url"]
    location_name = js["name"]

    add = js["address"]
    street_address = add["streetAddress"]
    city = add["addressLocality"]
    state = add["addressRegion"]
    zip_code = add["postalCode"]
    country_code = add["addressCountry"]
    geo = js["geo"]
    latitude = geo["latitude"]
    longitude = geo["longitude"]
    phone = js["telephone"]
    if "00000" in phone:
        phone = ""
    if phone == "0000":
        phone = ""
    if phone == "000":
        phone = ""
    if phone == "00":
        phone = ""
    if phone == "0":
        phone = ""
    phone = phone.replace(" (Custo da chamada para rede movel nacional)", "")
    phone = phone.replace(" (Custo da chamada para rede fixa nacional)", "")
    location_type = js["@type"]
    if "coming soon" in location_name.lower():
        location_type = "Coming Soon"
    try:
        store_number = page_url.split("/")[-1]
    except:
        store_number = ""
    hours_of_operation = get_hours(js)

    item = SgRecord(
        locator_domain=DOMAIN,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_code,
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


def fetch_data(store_urls_flatten_list, sgw: SgWriter):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [
            executor.submit(fetch_records, urlnum, surl, sgw)
            for urlnum, surl in enumerate(store_urls_flatten_list[0:])
        ]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():
    store_urls_for_all_countries = get_store_urls_for_all_countries()
    test_store_urls_flatten_list = []
    for idxall, j in enumerate(store_urls_for_all_countries[0:]):
        logger.info(f"[{j[0][3]}: {len(j)}]")
        test_store_urls_flatten_list.extend(j)
    total_stores = len(test_store_urls_flatten_list)
    logger.info(f"[STORES COUNT: {total_stores}]")

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
        fetch_data(test_store_urls_flatten_list, writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
