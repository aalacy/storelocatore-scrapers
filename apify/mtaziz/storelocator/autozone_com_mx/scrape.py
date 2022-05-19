from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from datetime import datetime
from lxml import html
import time
import ssl
import random
import json


logger = SgLogSetup().get_logger(logger_name="autozone_com_mx")
locator_domain_url = " https://www.autozone.com.mx"
MAX_WORKERS = 6
MISSING = SgRecord.MISSING


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
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def convert_time_to_p(time_str):
    converted_time = None
    d = datetime.strptime(time_str, "%H%M")
    converted_time = d.strftime("%I:%M" " %p")
    return converted_time


def get_hoo(hoo_json):
    hoo = []
    for i in hoo_json:
        start = i["intervals"][0]["start"]
        start = convert_time_to_p(str(start))
        end = i["intervals"][0]["end"]
        end = convert_time_to_p(str(end))
        day = f"{i['day']} {start} - {end}"
        hoo.append(day)
    return ", ".join(hoo)


def fetch_records(lat, lng, sgw: SgWriter):
    try:
        url = f"https://www.autozone.com.mx/ubicaciones/search-embed.html?q={lat},{lng}"
        r = get_response(url)
        sel = html.fromstring(r.text, "lxml")
        lis = sel.xpath('//ol[contains(@class, "location-list-results")]/li')
        latlng_data = "".join(sel.xpath('//script[@id="js-map-config-dir-map"]/text()'))
        latlng_js = json.loads(latlng_data)
        locs = latlng_js["locs"]

        for idx, l in enumerate(lis):
            purl = l.xpath('.//a[contains(@href, ".html")]/@href')[0]
            page_url = ""
            if purl:
                page_url = f"https://www.autozone.com.mx/ubicaciones/{purl}"
            else:
                page_url = MISSING
            location_name = l.xpath(
                './/div[contains(@class, "location-card-title")]/text()'
            )
            location_name = "".join(location_name) if location_name else MISSING
            sta1 = l.xpath('.//span[contains(@class, "c-address-street-1")]/text()')
            sta1 = "".join(sta1) if sta1 else MISSING

            city = l.xpath('.//span[contains(@class, "c-address-city")]/text()')
            city = "".join(city) if city else MISSING

            state = l.xpath('.//span[contains(@class, "c-address-state")]/text()')
            state = "".join(state) if state else MISSING
            zc = l.xpath('.//span[contains(@class, "c-address-postal-code")]/text()')
            zc = "".join(zc) if zc else MISSING

            cc = l.xpath('.//*[contains(@class, "c-address")]/@data-country')
            cc = "".join(cc) if cc else MISSING
            phone = l.xpath('.//a[contains(@data-ya-track, "phonecall")]/text()')
            phone = "".join(phone) if phone else MISSING
            # text/template
            article = l.xpath('.//script[contains(@type, "text/template")]/text()')
            store_number = locs[idx]["id"]
            latitude = locs[idx]["latitude"]
            longitude = locs[idx]["longitude"]
            logger.info(f"Latitude: {latitude}")

            location_type = SgRecord.MISSING
            hoo_data = "".join(article)
            sel_hoo = html.fromstring(hoo_data, "lxml")
            hoo_raw = "".join(
                sel_hoo.xpath(
                    '//span[contains(@class, "c-location-hours-today")]/@data-days'
                )
            )
            hoo_json = json.loads(hoo_raw)
            hours_of_operation = ""
            try:
                hours_of_operation = get_hoo(hoo_json)
            except:
                hours_of_operation = MISSING
            rec = SgRecord(
                locator_domain="autozone.com.mx",
                page_url=page_url,
                location_name=location_name,
                street_address=sta1,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=cc,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=SgRecord.MISSING,
            )
            sgw.write_row(rec)
    except Exception as e:
        url1 = (
            f"https://www.autozone.com.mx/ubicaciones/search-embed.html?q={lat},{lng}"
        )
        logger.info(f"{url1} Please fix this Error >> {e}")


def fetch_data(sgw: SgWriter):
    search_mx = DynamicGeoSearch(
        country_codes=[SearchableCountries.MEXICO],
        expected_search_radius_miles=20,
        max_search_results=10,
        granularity=Grain_8(),
        use_state=False,
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        task = [executor.submit(fetch_records, lat, lng, sgw) for lat, lng in search_mx]
        for future in as_completed(task):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
