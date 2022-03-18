import json
import urllib.parse
import time
import random

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import tenacity

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

logger = SgLogSetup().get_logger(logger_name="tkmaxx_pl")


@retry(stop=stop_after_attempt(15), wait=tenacity.wait_fixed(10))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(5, 20))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP Success Status: {response.status_code}")
            return response

        raise Exception(f"{url} >>> Failure Error: {response.status_code}")


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


def get_data(idx, slug, sgw: SgWriter):

    page_url = urllib.parse.unquote(f"https://www.tkmaxx.pl{slug}").replace(" ", "_")
    try:
        r = get_response(page_url)
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
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code="PL",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    except Exception as e:
        raise Exception(f" {e} >> Error Encountered at {page_url}")


def fetch_data(sgw: SgWriter):
    LOCATION_URL = "https://www.tkmaxx.pl/znajdz-sklep"
    urls = get_urls(LOCATION_URL)
    with futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {
            executor.submit(get_data, idx, url, sgw): url
            for idx, url in enumerate(urls)
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.tkmaxx.pl/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
