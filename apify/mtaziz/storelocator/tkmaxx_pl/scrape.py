from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import tenacity
import json
import time
import random
from lxml import html
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

headers_custom = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "referer": "http://localhost:8888/",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

logger = SgLogSetup().get_logger(logger_name="tkmaxx_pl")
MISSING = SgRecord.MISSING
LOCATION_URL = "https://www.tkmaxx.pl/znajdz-sklep"
MAX_WORKERS = 8


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(30), reraise=True)
def get_response_simple(url, headers_custom):
    with SgRequests() as http:
        r = http.get(url, headers=headers_custom)
        if r.status_code == 200:
            logger.info(f"HttpStatusCode: {r.status_code} for {url} ")
            return r
        raise Exception(f"Please GetResponseError at {url}")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(30))
def get_response(url):
    with SgRequests() as http:
        r = http.get(url, headers=headers)
        try:
            if r.status_code == 200:
                logger.info(f"HTTP status code: {r.status_code} for {url}")
                return r
            raise Exception(f"Please fix {url}")
        except Exception as e:
            raise Exception(f"Please fix it {e} | {url}")


def get_urls(loc_url):
    urls = []
    r = get_response(loc_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'markers')]/text()"))
    text = text.split('"markers":')[1].split("],")[0] + "]"
    js = json.loads(text)
    for j in js:
        source = j.get("text")
        root = html.fromstring(source)
        urls.append("".join(root.xpath("//a/@href")))

    return urls


def fetch_records():
    urls = get_urls(LOCATION_URL)
    for idx, slug in enumerate(urls[0:]):
        page_url = f"https://www.tkmaxx.pl{slug}"
        logger.info(f"Page URL: {page_url}")
        try:

            r = get_response_simple(page_url, headers_custom)
            time.sleep(random.randint(3, 10))
            logger.info(f"[{r.status_code}] Pulling the data from {page_url}")
            tree = html.fromstring(r.text)
            d = tree.xpath("//div[@class='nearby-store active-store']")[0]
        except:
            return

        location_name = "".join(d.xpath("./a/text()")).strip()
        store_number = "".join(d.xpath("./@data-store-id"))
        latitude = "".join(d.xpath("./@data-latitude"))
        longitude = "".join(d.xpath("./@data-longitude"))
        b = d.xpath("./following-sibling::div[1]")[0]
        street_address = "".join(
            b.xpath(".//p[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(b.xpath(".//p[@itemprop='addressLocality']/text()")).strip()
        postal = "".join(b.xpath(".//p[@itemprop='zipCode']/text()")).strip()
        phone = "".join(b.xpath(".//p[@itemprop='telephone']/text()")).strip()
        logger.info(f"[{idx}] Phone: {phone}")
        try:
            hours_of_operation = b.xpath(".//span[@itemprop='openingHours']/text()")[
                0
            ].strip()
        except IndexError:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=MISSING,
            zip_postal=postal,
            country_code="PL",
            store_number=store_number,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain="tkmaxx.pl",
            hours_of_operation=hours_of_operation,
        )

        yield row


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
