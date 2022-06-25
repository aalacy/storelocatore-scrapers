from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
import ssl

MAX_WORKERS = 2
try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

STORE_LOCATOR = "https://www.yha.org.uk/hostels/all-youth-hostels"
logger = SgLogSetup().get_logger("yha_org_uk")


def get_hostel_urls():
    with SgRequests(proxy_country="gb") as session:
        sl_r = session.get(STORE_LOCATOR, headers=headers)
        logger.info(f"Store Locator HTTP Status: {sl_r.status_code}")
        sel = html.fromstring(sl_r.text, "lxml")
        sel.xpath('//li/a[contains(@href, "/hostel/")]/@href')
        hostel_slugs = sel.xpath('//li/a[contains(@href, "/hostel/")]/@href')
        hostel_urls = []
        for i in hostel_slugs:
            if "https" not in i:
                purl = "https://www.yha.org.uk" + i
                hostel_urls.append(purl)
            else:
                hostel_urls.append(i)

        return hostel_urls


def fetch_records(idx, store_url, sgw: SgWriter):
    with SgRequests(
        proxy_country="gb",
    ) as http:
        r1 = http.get(store_url, headers=headers)
        logger.info(f"[{idx}] PullingContentFrom {store_url}")
        logger.info(f"[{idx}] HTTPStatus: {r1.status_code}")
        sel1 = html.fromstring(r1.text, "lxml")
        locname = sel1.xpath('//*[@class="hero__title"]/text()')
        locname = "".join(locname)
        xpath_new_for_add = '//div[contains(@class, "map-overlay__section")]/a[@class="location anchor-link"]/text()'
        add = sel1.xpath(xpath_new_for_add)
        add_raw = " ".join("".join(add).split())
        street_address = ""
        city = ""
        state = ""
        zip_ = ""
        pai = parse_address_intl(add_raw)
        sta1 = pai.street_address_1
        sta2 = pai.street_address_2

        if sta1 is not None and sta2 is not None:
            street_address = sta1 + ", " + sta2
        elif sta1 is not None and sta2 is None:
            street_address = sta1
        elif sta1 is None and sta2 is not None:
            street_address = sta2
        else:
            street_address = ""

        if pai.city is not None:
            city = pai.city
        if pai.postcode is not None:
            zip_ = pai.postcode

        if pai.state is not None:
            state = pai.state

        hours = ""
        try:
            hr = sel1.xpath(
                '//p[strong[contains(text(), "Reception opening hours")]]/text()'
            )
            hours = "".join(hr).strip()
        except:
            pass

        ph = ""

        try:
            ph = sel1.xpath('//p[contains(text(), "Phone")]/a/text()')[0]
        except:
            pass

        latlng = (
            sel1.xpath('//p[contains(text(), "Lat/Lng")]/text()')[0]
            .replace("Lat/Lng:", "")
            .strip()
        )
        ll = latlng.split(", ")
        lat = ll[0]
        lng = ll[1]

        if "Brecon, Powys, LD3 8NH" in add_raw:
            city = "Brecon"
        if "Brecon, Powys, LD3 7YS" in add_raw:
            city = "Brecon"
        item = SgRecord(
            page_url=store_url,
            location_name=locname,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_,
            store_number="",
            latitude=lat,
            longitude=lng,
            country_code="UK",
            phone=ph,
            locator_domain="yha.org.uk",
            hours_of_operation=hours,
            raw_address=add_raw,
        )
        logger.info(f"Item: {item.as_dict()}")
        sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    store_urls = get_hostel_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx, store_url, sgw)
            for idx, store_url in enumerate(store_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
