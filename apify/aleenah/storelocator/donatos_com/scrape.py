from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
from lxml import html


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "donatos.com"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("donatos_com")
MAX_WORKERS = 5

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(15))
def get_response(url):
    with SgRequests(timeout_config=600) as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")  # noqa
            return response
        raise Exception(
            f"{url} Please fix GetResponseError or HttpCodeError: {response.status_code}"
        )


def fetch_records(num, link, sgw: SgWriter):
    try:
        logger.info(f"[{num}] Pulling data from {link}")  # noqa
        r = get_response(link)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.find("main", {"id": "location-details"})
        try:
            title = div.find("h2").text
        except:
            return
        street = div.find("span", {"itemprop": "streetAddress"}).text
        city = div.find("span", {"itemprop": "addressLocality"}).text
        state = div.find("span", {"itemprop": "addressRegion"}).text
        pcode = div.find("span", {"itemprop": "postalCode"}).text
        phone = div.find("dd", {"itemprop": "phone"}).text
        lat = r.text.split('data-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-lng="', 1)[1].split('"', 1)[0]
        store = div.find("a", {"class": "btn"})["href"].split("=", 1)[1]
        hours = (
            div.text.split("Hours", 1)[1]
            .split("Order ", 1)[0]
            .replace("\n", " ")
            .strip()
        )

        rec = SgRecord(
            locator_domain="donatos.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )
        sgw.write_row(rec)
    except Exception as e:
        logger.info(f"Fix FetchRecordsError: << {e} >> << {num} | {link} >>")


def get_store_urls():
    all_store_url = "https://www.donatos.com/locations/find?address=300&mode=&redirect="
    rall = get_response(all_store_url)
    sel = html.fromstring(rall.text, "lxml")
    locurls = sel.xpath(
        '//*[contains(@href, "https://www.donatos.com/locations")]/@href'
    )
    locurls_dedup = list(set(locurls))
    locurls_dedup = sorted(locurls_dedup)
    return locurls_dedup


def fetch_data(sgw: SgWriter):
    store_urls = get_store_urls()
    logger.info(f"Total Store Urls: {len(store_urls)}")  # noqa
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, num, link, sgw)
            for num, link in enumerate(store_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
