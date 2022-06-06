from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
from io import BytesIO
from sgpostal.sgpostal import parse_address_usa
from lxml import html
import json
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MAX_WORKERS = 6
URL_LOCATION = "https://www.jamesavery.com/sitemap.xml.gz"
logger = SgLogSetup().get_logger("jamesavery_com")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def parse_address(raw_address):
    formatted_addr = parse_address_usa(raw_address)
    sta1 = formatted_addr.street_address_1
    sta2 = formatted_addr.street_address_2
    sta = ""
    if sta1 is not None and sta2 is not None:
        sta = sta1 + ", " + sta2
    elif sta1 is not None and sta2 is None:
        sta = sta1
    elif sta1 is None and sta2 is not None:
        sta = sta2
    else:
        sta = ""

    sta = sta.replace("Ste", "Suite")
    city = ""
    if formatted_addr.city is not None:
        city = formatted_addr.city

    state = ""
    if formatted_addr.state is not None:
        state = formatted_addr.state

    zip_code = ""
    if formatted_addr.postcode is not None:
        zip_code = formatted_addr.postcode
    return sta, city, state, zip_code


def get_store_urls():
    with SgRequests() as http:
        r = http.get(URL_LOCATION, headers=headers)
        sitemap = gzip.GzipFile(fileobj=BytesIO(r.content)).read()
        sel = html.fromstring(sitemap, "lxml")
        store_urls = sel.xpath('//loc[contains(text(), "store_locations")]/text()')
        store_urls = [i for i in store_urls if "://store_locations" not in i]
        return store_urls


def get_hours(sel):
    store_location_details = sel.xpath(
        '//div[@class="store-locations__details"]//text()'
    )
    store_location_details1 = [" ".join(i.split()) for i in store_location_details]
    store_location_details2 = [i for i in store_location_details1 if i]
    hours = " ".join(store_location_details2)
    hours = hours.split("Contact Us")[0].split("Hours")[-1]
    return hours


def fetch_records(idx, url, sgw: SgWriter):
    with SgRequests() as http:
        logger.info(f"PullingContentFrom: {url}")
        r = http.get(url, headers=headers)
        sel = html.fromstring(r.text)
        xpath_map = '//div[@class="store-locations__map"]/@data-google-map'
        page_url = url
        ra = sel.xpath('//p[@class="store-locations__detail"]/text()')
        raw_add = ", ".join(ra)

        sta, city, state, zip_code = parse_address(raw_add)

        coords = sel.xpath(xpath_map)[0]
        coords = json.loads(coords)["coordinates"]
        lat = coords[0][0]
        lng = coords[0][1]
        coords = sel.xpath(xpath_map)[0]
        coords = json.loads(coords)["coordinates"]
        lat = coords[0][0]
        lng = coords[0][1]
        ln = "".join(sel.xpath('//meta[@name="description"]/@content'))
        ln = ln.split(",")[0]
        tel = "".join(
            sel.xpath(
                '//div[@class="store-locations__details"]//a[contains(@href, "tel:")]/text()'
            )
        )
        hoo = get_hours(sel)
        hoo = hoo.replace(" Curbside hours vary by store; please call to confirm.", "")
        item = SgRecord(
            locator_domain="jamesavery.com",
            page_url=page_url,
            location_name=ln,
            street_address=sta,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="US",
            store_number="",
            latitude=lat,
            longitude=lng,
            hours_of_operation=hoo,
            phone=tel,
            raw_address=raw_add,
        )
        sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    loc_url_list = get_store_urls()
    logger.info(f"Total stores: {len(loc_url_list)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_ = [
            executor.submit(fetch_records, idx, url, sgw)
            for idx, url in enumerate(loc_url_list[0:])
        ]
        tasks.extend(task_)
        for future in as_completed(tasks):
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
