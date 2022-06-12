from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
import tenacity
from tenacity import retry, stop_after_attempt
from sgpostal.sgpostal import parse_address_intl
from lxml import html
import json
import ssl
import re
import time
import random


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="worldportsource_com")
MISSING = SgRecord.MISSING
DOMAIN = "worldportsource.com"
MAX_WORKERS = 10
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


@retry(stop=stop_after_attempt(3), wait=tenacity.wait_fixed(5))
def get_response(urlnum, url):
    with SgRequests() as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.get(url, headers=HEADERS)
        time.sleep(random.randint(1, 5))
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def get_country_name(sel):
    country_names = sel.xpath('//td[a[contains(@href, "/ports/index")]]/a/text()')
    return country_names


def get_country_based_map_url(sel):
    xpath_ports_index = '//td[a[contains(@href, "/ports/index")]]/a/@href'
    country_urls1 = sel.xpath(xpath_ports_index)
    base_url2 = "http://www.worldportsource.com"
    country_map_urls = [f'{base_url2}{i.replace("/index", "")}' for i in country_urls1]
    return country_map_urls


def get_store_count(sel):
    store_count = sel.xpath('//td[a[contains(@href, "/ports/index")]]/text()')
    store_count = ["".join(i.split()) for i in store_count]
    store_count = [i for i in store_count if i]
    store_count = [i.replace(")", "").replace("(", "") for i in store_count]
    return store_count


def get_country_map_urls():
    map_urls = []
    countries_url = "http://www.worldportsource.com/countries.php"
    r = get_response(0, countries_url)
    sel = html.fromstring(r.text, "lxml")
    country_map_urls = get_country_based_map_url(sel)
    country_names = get_country_name(sel)
    store_count = get_store_count(sel)
    for idx, cmurl in enumerate(country_map_urls):
        map_urls.append((country_names[idx], store_count[idx], cmurl))
    return map_urls


def get_store_url_per_country(idx, name_url):
    store_urls = []
    country_name = name_url[0]
    store_count = name_url[1]
    logger.info(f" {country_name} | Store Count: {store_count}")
    url = name_url[2]
    r2 = get_response(idx, url)
    jportdata = re.findall(r"jPortData(.*)\]", r2.text)
    jportdata1 = "".join(jportdata)
    jportdata2 = jportdata1.strip().lstrip("=").strip() + "]"
    jpd = json.loads(jportdata2)
    for _ in jpd:
        d = {}
        uri = _["uri"]
        d["country_name"] = country_name
        d["country_map_url"] = url
        d["page_url"] = f"http://www.worldportsource.com/ports/{uri}"
        store_urls.append(d)
    return store_urls


def get_us_ca_gb_store_urls():
    store_urls = []
    country_map_urls = get_country_map_urls()
    with ThreadPoolExecutor(max_workers=6, thread_name_prefix="fetcher") as ex:
        futures = [
            ex.submit(get_store_url_per_country, idx1, name_url)
            for idx1, name_url in enumerate(country_map_urls[0:])
        ]
        for fut in futures:
            try:
                for url in fut.result():
                    store_urls.append(url)
            except Exception as e:
                logger.info(f"Exception: {e}")
    return store_urls


def parse_address(raddress):
    pai = parse_address_intl(raddress)
    sa = pai.street_address_1
    street_address = sa if sa else MISSING
    city = pai.city
    city = city if city else MISSING
    state = pai.state
    state = state if state else MISSING
    zip_postal = pai.postcode
    zip_postal = zip_postal if zip_postal is not None else MISSING
    country_code = pai.country if pai.country else MISSING
    return street_address, city, state, zip_postal, country_code


def get_latlng_decimal(tlatlng):
    tlatlng_decimal = ""
    try:

        deg, minutes, seconds, direction = re.split("[°'\"]", tlatlng)
        tlatlng_decimal = (
            float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)
        ) * (-1 if direction in ["W", "S"] else 1)
    except:
        tlatlng_decimal = MISSING

    return tlatlng_decimal


def clean_data(raw_d):
    raw_d = [" ".join(i.split()) for i in raw_d]
    raw_d = [i for i in raw_d if i]
    if raw_d:
        raw_d = ", ".join(raw_d)
    else:
        raw_d = MISSING
    return raw_d


def get_lat(seld):
    lat = seld.xpath('//tr[th[contains(text(), "Latitude")]]/td/text()')
    lat = clean_data(lat)
    lat = get_latlng_decimal(lat)
    return lat


def get_lng(seld):
    lng = seld.xpath('//tr[th[contains(text(), "Longitude")]]/td/text()')
    lng = clean_data(lng)
    lng = get_latlng_decimal(lng)
    return lng


def get_location_name(seld):
    portname = seld.xpath('//tr[th[contains(text(), "Port Name")]]/td//text()')
    portname = clean_data(portname)
    return portname


def get_phone(seld):
    phone = seld.xpath('//tr[th[contains(text(), "Phone")]]/td//text()')
    phone = clean_data(phone)
    return phone


def get_loctype(seld):
    ptype = seld.xpath('//tr[th[contains(text(), "Port Type")]]/td//text()')
    ptype = clean_data(ptype)
    return ptype


def get_address(seld):
    add = seld.xpath('//tr[th[contains(text(), "Address")]]/td//text()')
    add = clean_data(add)
    sta, c, s, zp, cc = parse_address(add)
    return sta, c, s, zp, cc, add


def fetch_records(idx2, url_country, sgw: SgWriter):
    try:
        country = url_country["country_name"]
        logger.info(f"[{idx2}] | [{country}]")
        page_url = url_country["page_url"]
        rd = get_response(idx2, page_url)
        seld = html.fromstring(rd.text, "lxml")
        lat = get_lat(seld)
        lng = get_lng(seld)
        location_name = get_location_name(seld)
        phone = get_phone(seld)
        location_type = get_loctype(seld)
        street_address, city, state, zip_postal, country_code, ra = get_address(seld)
        if "MISSING" in street_address:
            street_address = location_name
        if "MISSING" in country_code:
            country_code = country
        store_number = page_url.split("/")[-1].split("_")[-1].replace(".php", "")
        rec = SgRecord(
            locator_domain=DOMAIN,
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
            latitude=lat,
            longitude=lng,
            hours_of_operation=MISSING,
            raw_address=ra,
        )
        sgw.write_row(rec)
    except Exception as e:
        logger.info(f"Please fix this {e} at {idx2} | {page_url} ")


def fetch_data(sgw: SgWriter):
    urls = get_us_ca_gb_store_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx2, url_country, sgw)
            for idx2, url_country in enumerate(urls[0:])
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
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
