from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import tenacity
import json
import urllib.parse
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
DOMAIN = "tkmaxx.pl"
MISSING = SgRecord.MISSING
LOCATION_URL = "https://www.tkmaxx.pl/znajdz-sklep"
MAX_WORKERS = 8


@retry(stop=stop_after_attempt(20), wait=tenacity.wait_fixed(5))
def get_response_pu(url):
    with SgRequests(verify_ssl=False) as http:
        r = http.get(url, headers=headers_custom)
        try:
            if r.status_code == 200:
                try:
                    if "website has not been found" not in r.text:
                        tree = html.fromstring(r.text)
                        d = tree.xpath("//div[@class='nearby-store active-store']")[0]
                        location_name = "".join(d.xpath("./a/text()")).strip()
                        logger.info(
                            f"HTTP status code for PAGE URL: {r.status_code} for {url} | {location_name}"
                        )
                        return r
                    raise Exception(f"Please fix the issue of redirection{url}")
                except Exception as e:
                    raise Exception(f"Please fix it {e} | {url}")
            raise Exception(f"Please fix {url}")
        except Exception as e:
            raise Exception(f"Please fix it {e} | {url}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
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


def fetch_records(idx, slug, sgw: SgWriter):
    page_url = urllib.parse.unquote(f"https://www.tkmaxx.pl{slug}").replace(" ", "_")

    try:
        r = get_response_pu(page_url)
        time.sleep(random.randint(10, 20))
        logger.info(f"Pulling the data from {page_url}")

        try:
            tree = html.fromstring(r.text)
            d = tree.xpath("//div[@class='nearby-store active-store']")[0]
        except IndexError:
            return
        except AttributeError:
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
            locator_domain=DOMAIN,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    except Exception as e:
        raise Exception(f" {e} >> Error Encountered at {page_url}")


def fetch_data(sgw: SgWriter):
    urls = get_urls(LOCATION_URL)
    logger.info(f"Total Store Count: {len(urls)}")
    with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(fetch_records, idx, url, sgw): url
            for idx, url in enumerate(urls[0:])
        }
        for future in futures.as_completed(future_to_url):
            if future.result() is not None:
                future.result()


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
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
